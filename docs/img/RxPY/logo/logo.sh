#!/bin/sh
inkscape RxPY-master.svg --export-area-page --export-plain-svg=RxPY.svg
inkscape RxPY-master.svg --export-area-page --export-png=RxPY_Logo_Big.png -w 560 -h 560
inkscape RxPY-master.svg --export-area-page --export-png=RxPY.png -w 150 -h 150

inkscape RxPY_Icon.svg --export-area-page --export-png=RxPY_Icon.png -w 128 -h 128

convert RxPY_Icon.png -define icon:auto-resize=64,48,32,16 RxPY.ico
