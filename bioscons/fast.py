"""
Some tips from http://www.scons.org/wiki/GoFastButton
"""
import SCons

def fast(env):
    """
    Given an :class:`SCons.Script.Environment`, set some flags for faster builds:

    * Caching of implicit dependencies
    * Use MD5-timestamp decider (if timestamp unchanged, don't checksum)
    * Clear the default environment. Requires use of ``env.Command(...)``, rather than bare ``Command(...)``
    """
    # cache implicit dependencies
    env.SetOption('implicit_cache', 1)
    env.Decider('MD5-timestamp')
    SCons.Defaults.DefaultEnvironment(tools = [])
