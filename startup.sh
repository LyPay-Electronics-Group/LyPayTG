#!/usr/bin/env bash
bad_parsing() {
    echo "parsing went wrong, press 'enter' to exit"
    read -r
    exit 1
}
check_before_start() {
    if [[ ! -f ".req" ]]; then
        echo "can't find '.req' file in current directory, press 'enter' to exit"
        read -r
        exit 1
    fi
    echo "checking for dependencies..."
    sleep 1
    python3 -m pip install -r .req
    echo "done"
    echo "checking for gnome-terminal profile..."
    sleep 1
    install_profile
    echo "done"
}
install_profile() {
    set -e
    PROFILE_NAME="LyPay"
    BG_COLOR="rgb(0,0,0)"
    FG_COLOR="rgb(205,214,244)"
    PALETTE="['rgb(0,0,0)','rgb(187,0,0)','rgb(0,187,0)','rgb(187,187,0)','rgb(0,107,187)','rgb(187,0,187)','rgb(0,187,187)','rgb(204,204,204)','rgb(128,128,128)','rgb(255,0,0)','rgb(0,255,0)','rgb(255,255,0)','rgb(92,92,255)','rgb(255,0,255)','rgb(0,255,255)','rgb(255,255,255)']"
    PROFILES=$(gsettings get org.gnome.Terminal.ProfilesList list)
    PROFILE_EXISTS_UUID=""
    for u in $(echo "$PROFILES" | grep -oE "[a-f0-9-]{36}"); do
        NAME=$(gsettings get org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$u/ visible-name | tr -d "'")
        if [[ "$NAME" == "$PROFILE_NAME" ]]; then
            PROFILE_EXISTS_UUID="$u"
            break
        fi
    done
    if [[ -n "$PROFILE_EXISTS_UUID" ]]; then
        echo "profile '$PROFILE_NAME' already exists: $PROFILE_EXISTS_UUID"
        return
    fi
    UUID=$(uuidgen)
    echo "'$PROFILE_NAME' (UUID: $UUID)"
    gsettings set org.gnome.Terminal.ProfilesList list \
    "$(echo "$PROFILES" | sed "s/]$/, '$UUID']/")"
    BASE_PATH="org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$UUID/"
    gsettings set $BASE_PATH default-size-columns 120
    gsettings set $BASE_PATH default-size-rows 32
    gsettings set $BASE_PATH visible-name "'$PROFILE_NAME'"
    gsettings set $BASE_PATH use-theme-colors false
    gsettings set $BASE_PATH background-color "'$BG_COLOR'"
    gsettings set $BASE_PATH foreground-color "'$FG_COLOR'"
    gsettings set $BASE_PATH palette "$PALETTE"
    gsettings set $BASE_PATH cursor-blink-mode "on"
    gsettings set $BASE_PATH use-system-font false
    gsettings set $BASE_PATH font "'Ubuntu Mono 12'"
}
launch() {
    if [[ "$1" == "p" ]]; then
        gnome-terminal --profile="LyPay" --title="LyPay: $3" -- bash -i -c "python3 \"$2\" \"$4\"; exec bash"
    elif [[ "$1" == "b" ]]; then
        gnome-terminal --profile="LyPay" --title="LyPay: heartbeat" -- bash -i -c "bokeh serve --show \"$2\"; exec bash"
    fi
}


cd "$(dirname "$(readlink -f "$0")")" || exit 1

if [[ $# -eq 0 ]]; then
    check_before_start
    gnome-terminal --profile="LyPay" --title="LyPay Launcher" -- bash -i -c "python3 launcher.py; exec bash"
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        -core)
            [[ -z "$2" || -z "$3" || -z "$4" ]] && bad_parsing
            launch p "$2" "$3" "$4"
            shift 4
            ;;
        -beat)
            [[ -z "$2" ]] && bad_parsing
            launch b "$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done
exit 0