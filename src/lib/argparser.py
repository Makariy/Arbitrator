import argparse


main_parser = argparse.ArgumentParser(description='Manage.py deployment tool')
main_parser.add_argument('file', type=str, help='Executive file')
main_parser.add_argument('command', choices=[
                                'track',
                                'analyze',
                                'bot'
                            ],
                         type=str, help='Command to execute')

