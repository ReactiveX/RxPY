import pyb

class Lock(object):
    """Dummy lock object for schedulers that don't need locking"""
    
    def __init__(self):
    	self.state = None

    def __enter__(self):
        """Context management protocol"""
        if self.state:
        	print("Deadlock!")
        	pyb.enable_irq()
        	return

        self.state = pyb.disable_irq()
        print("state=%d" % self.state)
    
    def __exit__(self, type, value, traceback):
        """Context management protocol"""

        pyb.enable_irq(True)#state=self.state)