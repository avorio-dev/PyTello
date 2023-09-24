import submodules.PyUtils.Misc.SubmodulesUpdater as SubmodUpd


def update_submodules(project_name):
    SubmodUpd.update_submodules(project_name)


if __name__ == "__main__":
    project_name = "PyTello"
    update_submodules(project_name)
