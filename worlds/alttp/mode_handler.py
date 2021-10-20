"""Accumulate a dictionary of all options"""
import os
from importlib import import_module
from types import ModuleType


class ModeHandler:


    # TODO: Maybe do this dynamically
    # For each package we have in this world
    # If it has an options module, add the options from it

    @classmethod
    def build_options(cls, er: bool = False, doors: bool = False, replace_existing = False):
        """Aggregate the options provided in the world's enabled submodules"""

        all_opts = {}

        # Standard
        import worlds.alttp.standard.options as std_opts
        cls.add_options_to_from(all_opts, std_opts.options, replace_existing)

        # entrance randomizer
        if er:
            import worlds.alttp.entrance_randomizer.options as er_opts
            cls.add_options_to_from(all_opts, er_opts.options, replace_existing)

        # doors
        if doors:
            import worlds.alttp.doors.options as doors_opts
            cls.add_options_to_from(all_opts, doors_opts.options, replace_existing)

        return all_opts


    @staticmethod
    def add_options_to_from(dest, src, replace: bool):
        """Merge the two options dicts with conditional replace"""
        for key in src:
            # If it already exists and we don't want to replace, then skip it
            if key in dest and not replace:
                continue
            # Otherwise add it
            dest[key] = src[key]






