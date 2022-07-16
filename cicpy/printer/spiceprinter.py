from .designprinter import DesignPrinter
import re


class SpicePrinter(DesignPrinter):
    def __init__(self,filename,rules):
        super().__init__(filename,rules)
        self.cell = None
        self.allcells = dict()
        self.current_cell = None

    def startLib(self,name):
        self.openFile(name + ".spice")

    def endLib(self):
        self.closeFile()

    def skipCell(self,cell):

        #if(cell.isCell()):
        #    return True

        if(cell.ckt is None):
            return True

        if(cell.abstract):
            return True

        if(cell.physicalOnly):
            return True


        #if(cell.meta is None):
        #    return True

        return False

    def startCell(self,cell):


        self.current_cell = cell

        self.allcells[cell.name] = 1

        self.cell = cell
        nodes = self.translateNodes(cell.ckt.nodes)
        strports = " ".join(nodes)
        self.f.write(f"""
*-------------------------------------------------------------
* {cell.name} {cell.__class__}
*-------------------------------------------------------------
.SUBCKT {cell.name} {strports}
""")


    def printCell(self,c):
        if(self.skipCell(c)):
            return


        self.startCell(c)


        if(c.meta is not None and "spice" in c.meta):
            spice = c.meta["spice"]
            if(type(spice) is list):
                self.f.write( "\n".join(spice) + "\n")
            else:
                self.f.write(spice + "\n")
        else:
            try:
                for o in c.ckt.devices:
                    self.printDevice(o)

                for o in c.ckt.instances:
                    self.printInstance(o)

            except Exception as e:
                c.printToJson()
                raise(e)
        self.endCell(c)

    def endCell(self,cell):

        self.current_cell = None
        self.f.write(".ENDS\n")

    def printRect(self,rect):
        pass

    def printPort(self,port):
        return

    def printText(self,text):
        pass

    def printDevice(self,o):

        if("Mosfet" in o.classname):
            self.printMosfet(o)
        elif("Resistor" in o.classname):
            self.printResistor(o)

        pass

    def printResistor(self,o):
        pass

    def translateNodes(self,nodes):

        for i in range(0,len(nodes)):
            if(re.search("<|>",nodes[i])):

                nodes[i]  = nodes[i].replace("<","_").replace(">","")


        return nodes

    def printMosfet(self,o):

        odev = self.rules.device(o.deviceName)
        typename = odev["name"]

        propss = self.spiceProperties(odev,o)

        self.f.write(f"X{o.name} " + " ".join(self.translateNodes(o.nodes)) + f" {typename} {propss} \n")

        pass

    def spiceProperties(self,odev,o):

        propss = ""
        props = list()
        if("propertymap" in odev):
            ddict = dict()

            #- Go through propertymap and find all parameters
            for key in odev["propertymap"]:
                ddict[key] = dict()
                ddict[key]["val"] = o.properties[odev["propertymap"][key]["name"]]
                ddict[key]["str"] = odev["propertymap"][key]["str"]

            #- If a parameter is used in a string, then replace it
            for key in ddict:
                m = re.search("({\w+})",ddict[key]["str"])
                if(m):
                    for mg in m.groups():
                        rkey = re.sub("{|}","",mg)
                        if(rkey in ddict):
                            ddict[key]["str"] = re.sub(mg,str(ddict[rkey]["val"]),ddict[key]["str"])


            #- Write the properties
            for key in odev["propertymap"]:
                val = str(ddict[key]["val"]) + ddict[key]["str"]
                propss += f" {key}={val} "
        return propss

    def printInstance(self,o):

        if(o.subcktName not in self.allcells):
            print(f"Warning: Could not find cell {o.subcktName}")
        else:
            self.f.write(f"X{o.name} " + " ".join(self.translateNodes(o.nodes)) + f" {o.subcktName}\n")
        pass
