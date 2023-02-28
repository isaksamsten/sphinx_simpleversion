import re
import subprocess

from pkg_resources import parse_version
from sphinx import application, config

__version__ = "0.1.0"

DEFAULT_INCLUDE_BRANCH_PATTERN = r"(?P<version>\d+.\d+).X"
DEFAULT_DEVELOP_BRANCH = "master"


def get_current_branch():
    return (
        subprocess.run("git branch --show-current", stdout=subprocess.PIPE, shell=True)
        .stdout.decode()
        .strip()
    )


class Version:
    def __init__(self, *, version, is_current, is_released, url_base, name):
        self.is_released = is_released
        self.is_current = is_current
        self.version = version
        self.name = name
        self.url_base = url_base
        self.url = f"/{self.url_base}/index.html"

    def __repr__(self) -> str:
        return f"Version({self.name}, {self.url}, current={self.is_current})"

    def __lt__(self, other):
        return self.version < other.version


class Versions:
    def __init__(
        self,
        *,
        include_branch_pattern=DEFAULT_INCLUDE_BRANCH_PATTERN,
        develop_branch=DEFAULT_DEVELOP_BRANCH,
    ):
        self.include_branch_pattern = include_branch_pattern
        self.develop_branch = develop_branch
        self.current_branch = get_current_branch()

        self.versions = self.__sorted_versions()
        self.develop_version = Version(
            version=parse_version("1000000000.0.0"),
            is_released=False,
            is_current=self.current_branch == self.develop_branch,
            url_base="master",
            name="main",
        )
        if self.versions:
            self.stable_version = self.versions[0]
        else:
            self.stable_version = self.develop_version
            # If the develop version is the only version
            # we consider it as released.
            self.develop_version.is_released = True

        self.versions.insert(0, self.develop_version)
        current_version = [v for v in self.versions if v.is_current]
        self.current_version = current_version[0]

    def __new_version_from_branch(self, branch):
        match = re.match(self.include_branch_pattern, branch)
        if not match:
            raise ValueError(f"Unknown branch {branch}")

        version = parse_version(match.group("version"))
        name = f"{version.major}.{version.minor}"
        url_base = branch
        return Version(
            version=version,
            is_current=self.current_branch == branch,
            is_released=True,
            url_base=url_base,
            name=name,
        )

    def __versions_from_git(self):
        with subprocess.Popen(
            ["git branch --format '%(refname:short)'"],
            stdout=subprocess.PIPE,
            shell=True,
        ) as cmd:
            branches, _ = cmd.communicate()
            branches = [branch.strip() for branch in branches.decode().splitlines()]
            return [
                self.__new_version_from_branch(branch)
                for branch in branches
                if re.match(self.include_branch_pattern, branch)
            ]

    def __sorted_versions(self):
        versions = {}

        for version in self.__versions_from_git():
            major_minor = f"{version.version.major}.{version.version.minor}"
            if major_minor not in versions:
                versions[major_minor] = version
            else:
                old_version = versions[major_minor]
                if version > old_version:
                    versions[major_minor] = version

        return [value for _, value in sorted(versions.items(), reverse=True)]

    def __repr__(self) -> str:
        return f"Versions(current_version={self.current_version}, versions={self.versions})"


def init_version(app: application.Sphinx, config: config.Config):
    versions = Versions(
        include_branch_pattern=app.config.versions_include_branch_pattern,
        develop_branch=app.config.versions_develop_branch,
    )
    if hasattr(app.config, "html_context"):
        app.config.html_context["versions"] = versions
    else:
        app.config.html_context = {"versions": versions}


def setup(app: application.Sphinx):
    app.add_config_value(
        "versions_include_branch_pattern",
        DEFAULT_INCLUDE_BRANCH_PATTERN,
        rebuild="html",
        types=[str],
    )
    app.add_config_value(
        "versions_develop_branch",
        DEFAULT_DEVELOP_BRANCH,
        rebuild="html",
        types=[str],
    )
    app.connect("config-inited", init_version)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
