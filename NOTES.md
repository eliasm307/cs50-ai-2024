# Downloading code

Use `wget [url].[folder.zip]`

Example:
```
wget https://cdn.cs50.net/2023/fall/psets/7/songs.zip
```

Unzip using `unzip [folder.zip]`

Example:
```
unzip songs.zip
```

Example full command:

```
echo 'Getting files...' && wget [url].[folder.zip] && echo 'Unzipping...' && unzip [folder.zip] && rm -rf [folder.zip] && cd [folder]
```


```
url=https://cdn.cs50.net/ai/2023/x/projects/1/knights.zip && wget $url && unzip $(basename $url) && rm $(basename $url) && cd $(basename $url .zip)
```

defined a shortcut for this ie:

```
get50() {
    local url="$1"
    wget "$url" && unzip $(basename "$url") && rm $(basename "$url") && cd $(basename "$url" .zip)
}
```

Example:
```
get50 https://cdn.cs50.net/ai/2023/x/projects/1/knights.zip
```