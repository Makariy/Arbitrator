import argparse


tracker_parser = argparse.ArgumentParser(description='Tracker options', add_help=True)
tracker_parser.add_argument('-i', '--input', type=str, required=True, help="Exchange from")
tracker_parser.add_argument('-o', '--output', type=str, required=True, help="Exchange to")

main_parser = argparse.ArgumentParser(description='Manage.py deployment tool')
main_parser.add_argument('file', type=str, help='Executive file')
main_parser.add_argument('command', choices=[
                                'track',
                            ],
                         type=str, help='Command to execute')

