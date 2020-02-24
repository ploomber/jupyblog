"""
https://jupyter-client.readthedocs.io/en/stable/api/manager.html

https://stackoverflow.com/questions/9977446/connecting-to-a-remote-ipython-instance
https://stackoverflow.com/questions/33731744/executing-code-in-ipython-kernel-with-the-kernelclient-api
"""
import jupyter_client

km = jupyter_client.KernelManager()

km.start_kernel()
km.is_alive()

# vs blocking_client?
kc = km.blocking_client()

out = []


def output(msg):
    # print(msg['msg_type'])
    if msg['msg_type'] == 'stream':
        out.append(msg['content']['text'])
    elif msg['msg_type'] == 'execute_result':
        out.append(msg['content']['data']['text/plain'])


kc.execute_interactive('print("hi")', output_hook=output)
kc.execute_interactive('1 + 2', output_hook=output)
kc.execute_interactive('import numpy as np; np.random.rand()', output_hook=output)


print(out)

km.shutdown_kernel()
