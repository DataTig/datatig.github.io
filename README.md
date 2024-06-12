# datatig.github.io


## Develop locally

To build the Jekyll site:

```
docker run --rm   --volume="$PWD:/srv/jekyll:Z" -p 4000:4000 -it jekyll/builder:4 /bin/bash -c 'gem install webrick && jekyll serve'
```


To build the DataTig admin site:

```
pip install datatig
python -m datatig.cli build . --staticsiteoutput _site/datatig_for_this_website 
```

