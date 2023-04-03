# videopipe-viz

**Explainability in Multimodal Video AI through visualisation**

> At RTL, we have a video AI pipeline (face detection, credit detection, subtitling, thumbnail selection, image aesthetics, …). The results come out as json files that can be read by professional video editing software. We would also like to demo our video AI pipeline to non-video editors who do not / cannot use a video editing software. To that end, we would like to smartly visualize results from the AI pipeline in the .mp4 video itself with moviepy and ffmpeg.
> To realise this project, we will give you access to our cloud platform and data. We also will help you conduct surveys with our video editors and stakeholders to find out whether burned-in AI in videos actively increases trust in AI solutions.

## some inspiration

- [mediapipe](https://github.com/google/mediapipe)

## possible tools

- [ffmpeg](https://ffmpeg.org/)
- [moviepy](https://zulko.github.io/moviepy/)

## requirements

- takes in an `.mp4` and a `.json` as input
- this doesn't need to be blazing fast: for now the idea is to create visualizations after a video is processed, not at streaming time 
- [optional] modular: different outputs of videopipe can be shown to the user on the same video


## references

**Dynamic Object Scanning: Object-Based Elastic Timeline for Quickly Browsing First-Person Videos**  
*Seita Kayukawa, Keita Higuchi, Ryo Yonetani, Masanori Nakamura, Yoichi Sato, Shigeo Morishima*  
CHI 2018 (extended abstract) – [[paper](https://dl.acm.org/doi/pdf/10.1145/3170427.3186501)]
