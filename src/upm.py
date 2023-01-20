import ftplib, argparse, os, sys, json, shutil; from dotenv import load_dotenv; from io import BytesIO; load_dotenv()

class config(): None
class con()   : None
class args()  : None

## -- VAR -- ##
_host=os.getenv('HOST')
_port=os.getenv('PORT')
_config=f"{os.path.expanduser('~')}\\.upm\\upm.json" if os.name=="nt" else f"{os.path.expanduser('~')}/.upm/upm.json"


## -- ARGS -- ##
class args():
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("command")
        parser.add_argument("package", action="store", help="package", nargs='?')
        parser.add_argument("-r", "--repo", dest="repo", action="store", help="select a repo")
        args = parser.parse_args()
        self.cmd = args.command
        self.repo=args.repo
        self.pakg=args.package

## -- FTP -- ##
class con():
    def __init__(self, _host=_host, _port=_port):
        self.ftp=ftplib.FTP_TLS()
        self.ftp.set_debuglevel(0)
        self.ftp.connect(str(_host), int(_port))
        self.ftp.sendcmd('USER user')
        self.ftp.sendcmd('PASS none')
        self.deps=[]
        
    def downloadFiles(self,path,destination):
        try:
            self.ftp.cwd(path)
            os.chdir(destination)
        except OSError as e:
            pass
        except ftplib.error_perm:
            return False
        try: os.mkdir(destination[0:len(destination)])
        except: pass
        filelist=self.ftp.nlst()
        for file in filelist:
            try:
                self.ftp.cwd(path+file+"/")
                self.downloadFiles(path+file+"/",destination)
            except ftplib.error_perm:
                os.chdir(destination[0:len(destination)])
                with open(os.path.join(destination,file),"wb") as f:
                    self.ftp.retrbinary("RETR "+file, f.write)
        return True
        
    def isPkg(self, pkg):
        try:
            self.ftp.cwd(f'/ftp/pub/{pkg}/')
        except ftplib.error_perm:
            return False
        return True
        
    def getVs(self, pkg, version=None):
        try:
            self.ftp.cwd(f'/ftp/pub/{pkg}/')
        except ftplib.error_perm:
            return False
        vs=self.ftp.nlst()
        fvs=None
        if not version:
            fvs=max(vs)
        else:
            if version.startswith(">=") or version.startswith(">"):
                cond=version.replace(">=", "").replace(">", "")
                try: fvs=max(filter(lambda v: v >= cond, vs))
                except ValueError: pass 
            elif version.startswith("<=") or version.startswith("<"):
                cond=version.replace("<=", "").replace("<", "")
                try: fvs=max(filter(lambda v: v <= cond, vs))
                except ValueError: pass 
            else:
                cond=version.replace("==", "")
                try: fvs=filter(lambda v: v == cond, vs)   
                except ValueError: pass 
        if type(fvs) != int:
            try: fvs=max(vs)
            except ValueError: pass    
        return fvs
    
    def getPkg(self, pkg, version=None):
        exists=self.isPkg(pkg)
        if not exists: return False
        version=self.getVs(pkg, version)
        r = BytesIO()
        self.ftp.retrbinary(f'RETR /ftp/pub/{pkg}/{version}/pkg.json', r.write)
        pkgConf = json.loads(r.getvalue().decode())
        deps=pkgConf["dependencies"]
        for dep in deps:
            if dep not in self.deps and dep != pkg: 
                self.deps.append(dep)
                gdep=self.getPkg(dep, deps[dep])
                if not gdep: print(f"Dependency not found: {dep}")
        self.downloadFiles(f"/ftp/pub/{pkg}/{version}/src", os.path.expanduser('~') + f"/.upm/cache/{pkg}/src/") 
        self.downloadFiles(f"/ftp/pub/{pkg}/{version}/bin", os.path.expanduser('~') + f"/.upm/cache/{pkg}/bin/") 
        if os.name=="nt": os.system("cd " + os.path.expanduser('~') + f"/.upm/cache/{pkg}" + " && " + pkgConf['setup']['windows'])
        else: os.system("cd " + os.path.expanduser('~') + f"/.upm/cache/{pkg}" + " && " + pkgConf['setup']['posix'])
        for file in os.listdir(os.path.expanduser('~') + f"/.upm/cache/{pkg}/bin/"): shutil.copy(os.path.expanduser('~') + f"/.upm/cache/{pkg}/bin/" + file, os.path.expanduser('~') + f"/.upm/bin/" + file)
        print(f"{pkg} installed successfully!")
        return True

## -- CONF -- ##
class conf():
    def __init__(self):
        self.config=self.retrieveConfig()
    def setupConfig(self):
        conf={"default": _host+":"+_port}
        json.dump(conf, open(_config, "w"))
        try: os.mkdir(os.path.expanduser('~') + "/.upm/")
        except: pass
        try: os.mkdir(os.path.expanduser('~') + "/.upm/cache")
        except: pass
        try: os.mkdir(os.path.expanduser('~') + "/.upm/bin")
        except: pass
        bin=os.path.expanduser('~') + "/.upm/bin"
        if os.name=="nt": os.popen(f'setx path "%PATH%;{bin}"')
        


    def retrieveConfig(self):
        self.setupConfig() if not os.path.exists(_config) else None
        return json.load(open(_config, "r"))
        
    def addRepo(self, _N, _H, _P):
        self.config[_N] = _H+":"+_P
        json.dump(self.config, open(_config, "w"))
        
    def rmRepo(self, _N):
        try:
            del self.config[_N]
        except KeyError:
            pass
        json.dump(self.config, open(_config, "w"))





def main():
    config  =conf()
    argss   =args()
    hp=[_host,_port]
    if argss.repo:
        try:
            hp=config.retrieveConfig()[argss.repo].split(":")
        except:
            print(f"Repo name not found!! [{argss.repo}] - Using default one")
    conc    =con(hp[0], hp[1])
        
    #config.addRepo('google', 'google.com', '21')
    if argss.cmd.lower()=="get" and argss.pakg != None:
        splitted=""
        name=""
        pkk=argss.pakg
        if ">" in pkk and not '>=' in pkk: splitted=">" + pkk.split(">")[1]; name=pkk.split(">")[0]
        elif ">=" in pkk: splitted=">=" + pkk.split(">=")[1]; name=pkk.split(">=")[0]
        elif "<" in pkk and not '<=' in pkk: splitted="<" + pkk.split(">")[1]; name=pkk.split("<")[0]
        elif "<=" in pkk: splitted="<=" + pkk.split("<=")[1]; name=pkk.split("<=")[0]
        elif "==" in pkk: splitted="==" + pkk.split("==")[1]; name=pkk.split("==")[0]
        else: splitted=""; name=pkk
        conc.getPkg(name, splitted)
    conc.ftp.quit()
        
if __name__ == "__main__": main()