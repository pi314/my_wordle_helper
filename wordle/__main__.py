from . import wordle_ui

try:
    wordle_ui.main()
except KeyboardInterrupt:
    print('\033[1;30mKeyboardInterrupt\033[m')
except EOFError:
    print('\033[1;30mEOFError\033[m')
