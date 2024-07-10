import os

import taggeradder
import argparse

taggeradder.app.ApplicationCLI.run(argparse.Namespace(**{
    "path": ".noter.json",
    "tags": ["tag@A", "tag@B"],
    "configuration": "./debug.configuration.json",
}))

