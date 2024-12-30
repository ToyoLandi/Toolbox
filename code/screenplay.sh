#!/bin/bash
############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Converts .mov to .gif gracefully!"
   echo
   echo "Syntax: screenplay <input_mov_path> <output_gif_path> <scale>"
   echo "Note: 'scale' defines the max width resolution of the output.gif."
}


# =-=-=-=-=-=-=-=
# MAIN ()
# =-=-=-=-=-=-=-=

movInfile=$1
gifOutfile=$2
ffmpegScale=$3
complexFilter="[0:v] fps=12,scale=$ffmpegScale:-1,split [a][b];[a] palettegen [p];[b][p] paletteuse"

# Inputs Check
echo "Source : "$movInfile
echo "Output : "$gifOutfile
echo "Scale  : "$ffmpegScale
echo "=-=-=-=-=-=-=-=-=-=-=-=-=\n"

# Actual ffmpeg + gifsicle call here
_cmd="ffmpeg -i '$movInfile' -filter_complex \"$complexFilter\" -f gif -  | gifsicle --optimize=3 --delay=3 > '$gifOutfile'"
echo $ffmpegWComp
bash <<<"$_cmd"