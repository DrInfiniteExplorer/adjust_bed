from tkinter import *



from tkinter import Tk, W, E, END
from tkinter.ttk import Frame, Button, Entry, Style

def set(e, txt):
    e.delete(0, END)
    e.insert(0, txt)

def floaty(asd):
    if asd == "":
        return 0
    return float(asd)

class Adjuster(Frame):

    def __init__(self, width, height, values, offset, invertX, invertY):
        super().__init__()

        self.width = width
        self.height = height
        
        self.orientXIdx = lambda x: width-x-1 if invertX else x
        self.orientYIdx = lambda y: height-y-1 if invertY else y

        self.initUI(values, offset)

    def initUI(self, initVals, initOffset):

        self.master.title("Adjuster")

        Style().configure("TButton", padding=(0, 5, 0, 5),
        font='serif 10')

        for x in range(0, self.width+1):
            self.columnconfigure(x, pad=3)
        for y in range(0, self.height+2):
            self.rowconfigure(y, pad=3)

        self.fields = {}

        for y in range(0, self.height):
            for x in range(0, self.width):
                entry = Entry(self)
                set(entry, initVals[(self.orientXIdx(x),self.orientYIdx(y))])
                self.fields[(x,y)] = entry
                entry.grid(row=y, column=x)

        self.row_adjust = []
        self.columnconfigure(self.width, pad=10)
        for y in range(0, self.height):
            entry = Entry(self)
            self.row_adjust.append(entry)
            entry.grid(row=y, column=self.width)

        self.column_adjust = []
        self.rowconfigure(self.height, pad=10)
        for x in range(0, self.width):
            entry = Entry(self)
            self.column_adjust.append(entry)
            entry.grid(row=self.height, column=x)
        
        self.all_adjust = Entry(self)
        self.all_adjust.grid(row=self.height, column=self.width)
                
        self.z_field = Entry(self)
        set(self.z_field, initOffset)
        self.z_field.grid(row=self.height+1, column=0)

        self.write = Button(self, text="Write", command=self.write)
        self.write.grid(row=self.height+1, column=self.width)

        self.pack()
    
    def write(self):
    
        buff = []
        
        def out(str):
            buff.append(str)
        
        adjust_all = floaty(self.all_adjust.get())
        set(self.all_adjust, "")
            
        for y in range(0, self.height):
            row_adjust = self.row_adjust[y]
            y_adjust = floaty(row_adjust.get())
            
            for x in range(0, self.width):
                column_adjust = self.column_adjust[x]
                x_adjust = floaty(column_adjust.get())
                field = self.fields[(x,y)]
                value = format(floaty(field.get()) + x_adjust + y_adjust + adjust_all, '.5f')
                set(field, f"{value}")

        for x in range(0, self.width):
            set(self.column_adjust[x], "")
        for y in range(0, self.height):
            set(self.row_adjust[y], "")
            
        for y in range(0, self.height):
            out(f"; Row {y}")
            for x in range(0, self.width):
                value = self.fields[(self.orientXIdx(x), self.orientYIdx(y))].get()
                out(f"G29 S3 I{x} J{y} Z{value}")
        
        offset = self.z_field.get()
        out("; Z-offset")
        out(f"G29 S4 Z{offset}")
        
        out("M420 S1 ; Bed leveling")
        
        out("M420 V ; Report back the configuration")
        
        print("\n" * 5)
        print("\n".join(buff))
        
        with open("adjusted_bed.gco", "w") as f:
            f.write("\n".join(buff))

        vals = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                value = self.fields[(self.orientXIdx(x), self.orientYIdx(y))].get()
                row.append(format(floaty(value), "9.5f")) # Align output in file.
            vals.append(row)
        with open("bed.out", "w") as f:
            for row in vals:
                f.write(", ".join(row) + "\n")
            f.write(self.z_field.get() + "\n")
 

def main():

    cols = None
    rows = None
    z = None
    values = []
    with open("bed.txt", "r") as f:
        for line in f:
            vals = [float(word) for word in line.split(",")]
            if cols is None:
                cols = len(vals)
                values.append(vals)
            elif len(vals) == 1:
                z = vals[0]
                rows = len(values)
            elif len(vals) == cols:
                values.append(vals)
            else:
                error(f"I'm so confused about this file")
    valMap = {(x,y): value for y, row in enumerate(values) for x, value in enumerate(row)}

    root = Tk()
    app = Adjuster(width=cols, height=rows, values=valMap, offset=z, invertX=False, invertY=True)
    root.mainloop()


if __name__ == '__main__':
    main()