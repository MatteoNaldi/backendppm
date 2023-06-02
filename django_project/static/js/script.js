function shareToCopy(el, playlist_link){
    link = playlist_link.replace('detail', 'shared')
    navigator.clipboard.writeText(link);
    el.innerText='Copied';
}