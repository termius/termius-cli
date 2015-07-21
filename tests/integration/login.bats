#!/usr/bin/env bats

@test "login help by arg" {
  run serverauditor login --help
  [ "$status" -eq 0 ]
}

@test "login help command" {
  run serverauditor help login
  [ "$status" -eq 0 ]
}

@test "login by tester account" {
  if [ "$Serverauditor_username" == '' ] || [ "$Serverauditor_password" == '' ];then
      skip
  fi
  run serverauditor login --username $Serverauditor_username -p $Serverauditor_password
  echo $output
  [ "$status" -eq 0 ]
  ! [ -z $(cat ~/.serverauditor) ]
}
