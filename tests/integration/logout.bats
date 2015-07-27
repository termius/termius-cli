#!/usr/bin/env bats

@test "logout help by arg" {
  run serverauditor logout --help
  [ "$status" -eq 0 ]
}

@test "logout help command" {
  run serverauditor help logout
  [ "$status" -eq 0 ]
}

@test "login & logout by tester account" {
  if [ "$Serverauditor_username" == '' ] || [ "$Serverauditor_password" == '' ];then
      skip '$Serverauditor_username and $Serverauditor_password are not set!'
  fi

  rm ~/.serverauditor || true
  serverauditor login --username $Serverauditor_username -p$Serverauditor_password

  run serverauditor logout
  [ "$status" -eq 0 ]
  [ -z $(cat ~/.serverauditor) ]
}
