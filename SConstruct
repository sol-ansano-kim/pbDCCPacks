import os
env = Environment()


install_maya = True
dist_path = os.path.abspath(ARGUMENTS.get("dist", "release"))


try:
    install_maya = int(ARGUMENTS.get("install-maya", "1")) != 0
except:
    install_maya = True


if install_maya:
    env.Install(os.path.join(dist_path, "pbDCCPacks"), Glob("maya/*.py"))
    env.Install(os.path.join(dist_path, "pbDCCPacks"), Glob("maya/*.config"))
