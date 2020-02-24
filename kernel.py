import mistune
"""
https://jupyter-client.readthedocs.io/en/stable/api/manager.html

https://stackoverflow.com/questions/9977446/connecting-to-a-remote-ipython-instance
https://stackoverflow.com/questions/33731744/executing-code-in-ipython-kernel-with-the-kernelclient-api
"""
import jupyter_client


class JupyterSession:

    def __init__(self):
        self.km = jupyter_client.KernelManager()
        self.km.start_kernel()
        self.kc = self.km.blocking_client()
        self.out = []

    def output_hook(self, msg):
        # print(msg['msg_type'])
        if msg['msg_type'] == 'stream':
            self.out.append(msg['content']['text'])
        elif msg['msg_type'] == 'execute_result':
            self.out.append(msg['content']['data']['text/plain'])

    def execute(self, code):
        self.kc.execute_interactive(code,
                                    output_hook=self.output_hook)
        return self.out[-1]

    def __del__(self):
        self.km.shutdown_kernel()


session = JupyterSession()
session.execute('print("hi")')
session.execute('1 + 2')
session.execute('import numpy as np; np.random.rand()')

print(session.out)


markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
md = markdown("""
```python
1 + 1
```

# header

```python
2 + 2
```
""")

for e in md:
    if e['type'] == 'block_code':
        print('In: ', e['text'])
        print('>>> ', session.execute(e['text']))

del session
