from pathlib import Path
import re
import base64
import shutil
import queue
from collections import defaultdict
import logging

import jupyter_client

from jupyblog import models

logger = logging.getLogger(__name__)


class ASTExecutor:
    """Execute code chunks from a markdown ast
    """

    def __init__(self,
                 wd=None,
                 front_matter=None,
                 img_dir=None,
                 canonical_name=None):
        self._session = None
        self._front_matter = front_matter
        self._img_dir = img_dir
        self._canonical_name = canonical_name
        self.wd = wd if wd is None else Path(wd)

    def __call__(self, md_ast):

        logger.debug('Starting python code execution...')

        if self.wd:
            if not self.wd.exists():
                self.wd.mkdir(exist_ok=True, parents=True)

            self._session.execute('import os; os.chdir("{}")'.format(
                str(self.wd)))

        blocks = [e for e in md_ast if e['type'] == 'block_code']

        # info captures whatever is after the triple ticks, e.g.
        # ```python a=1 b=2
        # Info: "python a=1 b=1"

        # add parsed info
        blocks = [{**block, **parse_info(block['info'])} for block in blocks]

        for block in blocks:
            if block.get('info') and not block.get('skip'):
                output = self._session.execute(block['text'])
                logger.info('In:\n\t%s', block['text'])
                logger.info('Out:\n\t%s', output)
                block['output'] = output
            else:
                block['output'] = None

        logger.debug('Finished python code execution...')

        return blocks

    def __enter__(self):
        self._session = JupyterSession(front_matter=self._front_matter,
                                       img_dir=self._img_dir,
                                       canonical_name=self._canonical_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._session
        self._session = None


def parse_info(info):
    if info is not None:
        elements = info.split(' ')

        if len(elements) == 1:
            return {}

        return {
            t.split('=')[0]: t.split('=')[1]
            for t in elements[1].split(',')
        }
    else:
        return {}


class JupyterSession:
    """Execute code in a Jupyter kernel and parse results

    Examples
    --------
    >>> from jupyblog.execute import JupyterSession
    >>> s = JupyterSession()
    >>> s.execute('1 + 10')
    >>> del s # ensures kernel is shut down
    """

    # Reference for managing kernels
    # https://github.com/jupyter/jupyter_client/blob/5742d84ca2162e21179d82e8b36e10baf0f8d978/jupyter_client/manager.py#L660
    def __init__(self, front_matter=None, img_dir=None, canonical_name=None):
        self.km = jupyter_client.KernelManager()
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()
        self.out = defaultdict(lambda: [])
        self._front_matter = front_matter or models.FrontMatter()
        self._img_dir = img_dir
        self._canonical_name = canonical_name
        self._counter = 0

        # clean up folder with serialized images if needed
        if self._front_matter.jupyblog.serialize_images:
            serialized = Path(self._img_dir, self._canonical_name,
                              'serialized')

            if serialized.is_dir():
                shutil.rmtree(serialized)

    def execute(self, code):
        out = []
        self.kc.execute(code)

        while True:
            try:
                io_msg = self.kc.get_iopub_msg(timeout=10)
                io_msg_content = io_msg['content']
                if 'execution_state' in io_msg_content and io_msg_content[
                        'execution_state'] == 'idle':
                    break
            except queue.Empty:
                break

            if 'execution_state' not in io_msg['content']:
                out.append(io_msg)

        processed = [
            _process_content_data(
                o['content'],
                self._counter,
                idx,
                serialize_images=self._front_matter.jupyblog.serialize_images,
                img_dir=self._img_dir,
                canonical_name=self._canonical_name)
            for idx, o in enumerate(out)
        ]

        self._counter += 1
        return [content for content in processed if content]

    def __del__(self):
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)


PLAIN = 'text/plain'
HTML = 'text/html'
PNG = 'image/png'
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def extract_outputs_from_notebook_cell(outputs, prefix, serialize_images,
                                       img_dir, canonical_name):
    return [
        _process_content_data(out,
                              counter=prefix,
                              idx=idx,
                              serialize_images=serialize_images,
                              img_dir=img_dir,
                              canonical_name=canonical_name)
        for idx, out in enumerate(outputs)
    ]


def _process_content_data(content,
                          counter,
                          idx,
                          serialize_images=False,
                          img_dir=None,
                          canonical_name=None):
    """

    Parameters
    ----------
    content : list
        "outputs" key in a notebook's cell

    counter : str
        Prefix to apply to image paths. Only used if
        serialize_images=True

    idx : str
        Suffix to apply to the image path. Only used if
        serialize_images=True

    serialize_images : bool, default=False
        Serialize images as .png files. Otherwise, embed them as base64 strings

    img_dir : str, default=None
        Folder to serialize images. Only used if serialize_images=True

    canonical_name : str, default=None
        Used to construct the path to the images for this post:
        {img_dir}/{canonical_name}/serialized. Only used if
        serialize_images=True
    """

    if 'data' in content:
        data = content['data']

        if data.get('image/png'):
            image_base64 = data.get('image/png')

            if serialize_images:
                serialized = Path(img_dir, canonical_name, 'serialized')
                serialized.mkdir(exist_ok=True, parents=True)

                id_ = f'{counter}-{idx}'
                filename = f'{id_}.png'
                path_to_image = serialized / filename
                base64_2_image(image_base64, path_to_image)

                return (HTML, f'![{id_}](serialized/{filename})')
            else:
                return PNG, base64_html_tag(image_base64)
        if data.get('text/html'):
            return HTML, data.get('text/html')
        else:
            return PLAIN, data['text/plain']
    elif 'text' in content:
        out = content['text'].rstrip()

        if out[-1] != '\n':
            out = out + '\n'

        return PLAIN, out
    elif 'traceback' in content:
        return PLAIN, remove_ansi_escape('\n'.join(content['traceback']))


def remove_ansi_escape(s):
    """
    https://stackoverflow.com/a/14693789/709975
    """
    return ANSI_ESCAPE.sub('', s)


def base64_2_image(message, path_to_image):
    bytes = message.encode().strip()
    message_bytes = base64.b64decode(bytes)
    Path(path_to_image).write_bytes(message_bytes)


def base64_html_tag(base64):
    return f'<img src="data:image/png;base64, {base64.strip()}"/>'
