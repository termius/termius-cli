login_serverauditor () {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ];then
      skip '$SERVERAUDITOR_USERNAME and $SERVERAUDITOR_PASSWORD are not set!'
    fi

    serverauditor login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
}

pull_serverauditor() {
    login_serverauditor

    serverauditor pull -p $SERVERAUDITOR_PASSWORD

}

get_models_set() {
    cat ~/.serverauditor/storage | jq .$1
}

get_models_set_length() {
    cat ~/.serverauditor/storage | jq ".$1 | length"
}

get_model_field() {
  cat ~/.serverauditor/storage | jq ".$1" | jq ".[] | select(.${4:-id} == $2)" >&2
  cat ~/.serverauditor/storage | jq ".$1" | jq ".[] | select(.${4:-id} == $2)" | jq ".$3"
}

clean_storage() {
    rm ~/.serverauditor/storage
}
