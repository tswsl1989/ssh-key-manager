import argparse
import logging
import os
import shutil

import sshkeymanager as skm

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base", "-b", help="Base directory to search for keys", default="~/.ssh/keys"
    )
    ap.add_argument("--hostname", "-H", help="Hostname to search for", default=None)
    ap.add_argument(
        "--verbose",
        "-v",
        help="Output more information while running",
        action="count",
        default=0,
    )
    ap.add_argument(
        "--no-backup", "-n", help="Don't backup existing file", default=False
    )
    ap.add_argument(
        "--output", "-o", help="Output file name", default="~/.ssh/authorized_keys"
    )

    args = ap.parse_args()

    log = logging.getLogger("sshkeymanager")
    logLevel = logging.WARNING
    logLevel = max([10, logLevel - 10 * args.verbose])

    console = logging.StreamHandler()
    console.setLevel(logLevel)
    console.setFormatter(logging.Formatter("%(name)-12s:%(levelname)-8s - %(message)s"))
    log.addHandler(console)
    log.setLevel(logLevel)
    log.debug(f"Log level set to {logging.getLevelName(logLevel)}")

    basedir = os.path.expanduser(args.base)
    output = os.path.expanduser(args.output)

    key_opt_list = skm.build_key_list(basedir, args.hostname)

    if args.no_backup:
        log.info(f"Generating new key file into {output}")
        skm.make_authorized_key_files(key_opt_list, output)
    else:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            tfn = os.path.join(td, "skm-temp")
            log.info(f"Generating new key file into {tfn}")
            skm.make_authorized_key_files(key_opt_list, tfn)

            log.info(
                f"Backing up existing file (if any) from {output} to {output + '.bak'}"
            )
            try:
                shutil.move(output, output + ".bak")
            except FileNotFoundError:
                pass

            log.info(f"Moving generated file to {args.output}")
            shutil.move(tfn, output)
