#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
    private_key_content='private_key content'
    private_key_path=key
    echo $private_key_content > $private_key_path
}

teardown() {
    rm $private_key_path
}

@test "key help by arg" {
    run serverauditor key --help
    [ "$status" -eq 0 ]
}

@test "key help command" {
    run serverauditor help key
    [ "$status" -eq 0 ]
}

@test "Add general key" {
    run serverauditor key -L test -i $private_key_path
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 1 ]
    [ $(diff ~/.serverauditor/ssh_keys/test $private_key_path) = ""]
}

@test "Add many keys" {
    run serverauditor key -L test_1 -i $private_key_path
    run serverauditor key -L test_2 -i $private_key_path
    run serverauditor key -L test_3 -i $private_key_path
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 3 ]
    [ $(diff ~/.serverauditor/ssh_keys/test_1 $private_key_path) = ""]
    [ $(diff ~/.serverauditor/ssh_keys/test_2 $private_key_path) = ""]
    [ $(diff ~/.serverauditor/ssh_keys/test_3 $private_key_path) = ""]
}

@test "Update key" {
    key=$(serverauditor key -L test -i $private_key_path)
    run serverauditor key -i $private_key_path $key --debug
    echo ${lines[*]}
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 1 ]
    [ $(diff ~/.serverauditor/ssh_keys/key $private_key_path) = ""]
}

@test "Update many keys" {
    key1=$(serverauditor key -L test_1 -i key)
    key2=$(serverauditor key -L test_2 -i key)
    key3=$(serverauditor key -L test_3 -i key)
    run serverauditor key -i $private_key_path $key1 $key2 $key3
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 3 ]
    [ $(diff ~/.serverauditor/ssh_keys/test_1 $private_key_path) = ""]
    [ $(diff ~/.serverauditor/ssh_keys/test_2 $private_key_path) = ""]
    [ $(diff ~/.serverauditor/ssh_keys/test_3 $private_key_path) = ""]
}

@test "Delete key" {
    key=$(serverauditor key -L test_1 -i key)
    run serverauditor key --delete $key
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 0 ]
    ! [ -f ~/.serverauditor/ssh_keys/test_1 ]
}

@test "Delete many keys" {
    key1=$(serverauditor key -L test_1 -i key)
    key2=$(serverauditor key -L test_2 -i key)
    key3=$(serverauditor key -L test_3 -i key)
    run serverauditor key --delete $key1 $key2 $key3
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 0 ]
    ! [ -f ~/.serverauditor/ssh_keys/test_1 ]
    ! [ -f ~/.serverauditor/ssh_keys/test_2 ]
    ! [ -f ~/.serverauditor/ssh_keys/test_3 ]
}
