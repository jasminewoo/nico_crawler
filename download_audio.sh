youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' -o '~/Downloads/%(title)s-%(id)s.%(ext)s' -i -x $1
