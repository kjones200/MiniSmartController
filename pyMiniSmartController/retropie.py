# !/usr/bin/env python

"""
Retriopie
------------------------------------------------------------
Commmon definitions used by retropie



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR
ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR
OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

EMULATORS = ["amiga", "amstradcpc", "apple2", "arcade", "atari800", "atari2600", "atari5200", "atari7800",
             "atarilynx", "atarist", "c64", "coco", "dragon32", "dreamcast", "fba", "fds", "gamegear", "gb", "gba",
             "gbc", "intellivision", "macintosh", "mame-advmame", "mame-libretro", "mame-mame4all", "mastersystem",
             "megadrive", "msx", "n64", "neogeo", "nes", "ngp", "ngpc", "pc", "ports", "psp", "psx", "scummvm",
             "sega32x", "segacd", "sg-1000", "snes", "vectrex", "videopac", "wonderswan", "wonderswancolor",
             "zmachine", "zxspectrum"]

PROCESS_NAMES = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi", "linapple", "hatari", "stella",
                 "atari800", "xroar", "vice", "daphne", "reicast", "pifba", "osmose", "gpsp", "jzintv",
                 "basiliskll", "mame", "advmame", "dgen", "openmsx", "mupen64plus", "gngeo", "dosbox", "ppsspp",
                 "simcoupe", "scummvm", "snes9x", "pisnes", "frotz", "fbzx", "fuse", "gemrb", "cgenesis", "zdoom",
                 "eduke32", "lincity", "love", "alephone", "micropolis", "openbor", "openttd", "opentyrian",
                 "cannonball", "tyrquake", "ioquake3", "residualvm", "xrick", "sdlpop", "uqm", "stratagus",
                 "wolf4sdl", "solarus"]

PROCESS_NAMES_EXTRA = PROCESS_NAMES
PROCESS_NAMES_EXTRA.append("emulationstation")
PROCESS_NAMES_EXTRA.append("emulationstatio")

# Base directories
ROM_BASE = '/home/pi/RetroPie/roms/'
EMULATOR_BASE = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ "

