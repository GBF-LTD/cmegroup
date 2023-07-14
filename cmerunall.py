#%%
import sys

portland_dir = r"C:/Users/YuriPereria/.vscode/VSCODE/Portland"
sys.path.append(portland_dir)

import portlandnational as pl
import portlandtogit1 as pln
import ET as et
import britishpound as bp
import GXgasoil as goil
import MGOM1B as mgo
import NYHARBORULSDMP as ny
import ULSD10ppmdiffTP as ulsd

def main():
    pl.main()
    pln.main()
    et.main()
    ulsd.main()
    ny.main()
    mgo.main()
    goil.main()
    bp.main()
    print("Upload Complete")


if __name__ == "__main__":
    main()




