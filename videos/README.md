# How to generate videos from the images?

From the `output/` directory, run the following.

```
ffmpeg -f image2 -r 1 -i %05d.png -vcodec mpeg4 -y movie.mp4
```