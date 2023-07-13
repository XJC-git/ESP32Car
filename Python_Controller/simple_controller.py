import keyword

import keyboard as keyboard


def abc(x):
	print(x)


if __name__ == "__main__":
	keyboard.hook(abc)
	keyboard.wait()