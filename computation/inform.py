class InformFile:
    def __init__(self, filename=None):
        self.density = None
        self.R = None
        self.StepsPerRev = None
        self.filename = None

        if filename is not None:
            self.set_file_name(filename)

    def set_file_name(self, filename):
        self.filename = filename
        if isinstance(self.filename, str) and len(self.filename) > 0:
            self.read()

    def read(self):
        d = {}
        with open(self.filename) as file:
            for line in file:
                tmp = line.rstrip('\n')
                tmp = tmp.split('=')

                if len(tmp) > 1:
                    try:
                        try:
                            val = self.force_int_unless_float(tmp[1])
                        except:
                            val = eval(tmp[1], dict(d))

                        d[tmp[0]] = val
                        setattr(self, tmp[0], val)
                    except:
                        print('setting %s failed' % tmp[0])

        # Explicitly set values...!
        self.density = 1.224
        self.R = self.size
        self.StepsPerRev = self.StepsPerPi * 2

    @staticmethod
    def force_int_unless_float(s):
        f = float(s)
        i = int(f)
        return i if i == f else f
