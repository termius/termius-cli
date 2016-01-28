
login_serverauditor () {
    if [ "$Serverauditor_username" == '' ] || [ "$Serverauditor_password" == '' ];then
      skip '$Serverauditor_username and $Serverauditor_password are not set!'
    fi

    serverauditor login --username $Serverauditor_username -p $Serverauditor_password
}

pull_serverauditor() {
    login_serverauditor

    serverauditor pull -p $Serverauditor_password

}
