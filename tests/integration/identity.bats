#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
    private_key_content='private_key content'
    private_key_path=key1
    echo -n $private_key_content > $private_key_path

    second_key_content='second_key content'
    second_key_path=key2
    echo -n $second_key_content > $second_key_path
}

teardown() {
    rm $private_key_path
    rm $second_key_path
}


@test "Identity help by arg" {
    run serverauditor identity --help
    [ "$status" -eq 0 ]
}

@test "Identity help command" {
    run serverauditor help identity
    [ "$status" -eq 0 ]
}

@test "Add general identity" {
    run serverauditor identity -L local --username 'ROOT' --password 'pa'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    ssh_identity=${lines[1]}
    [ "$(get_model_field 'sshidentity_set' $ssh_identity 'label')" = '"local"' ]
    [ "$(get_model_field 'sshidentity_set' $ssh_identity 'username')" = '"ROOT"' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'is_visible') = 'true' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'ssh_key') = 'null' ]
}

@test "Add identity with key" {
    run serverauditor identity -L local --identity-file $private_key_path --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 1 ]
    ssh_identity=${lines[1]}
    [ "$(get_model_field 'sshidentity_set' $ssh_identity 'label')" = '"local"' ]
    [ "$(get_model_field 'sshidentity_set' $ssh_identity 'username')" = 'null' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'is_visible') = 'true' ]
    ssh_key=$(get_model_field 'sshidentity_set' $ssh_identity 'ssh_key')
    [ $(get_model_field 'sshkeycrypt_set' $ssh_key 'label') = '"key1"' ]
    [ "$(get_model_field 'sshkeycrypt_set' $ssh_key 'private_key')" = "\"$private_key_content\"" ]
}

@test "Update identity" {
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity --password 'ps' $identity
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    [ "$(get_model_field 'sshidentity_set' $identity 'label')" = '"local"' ]
    [ "$(get_model_field 'sshidentity_set' $identity 'username')" = '"ROOT"' ]
    [ "$(get_model_field 'sshidentity_set' $identity 'password')" = '"ps"' ]
    [ $(get_model_field 'sshidentity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'sshidentity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update many identities" {
    identity1=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    identity2=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity -L local --username 'ROOT' --password 'pa' $identity1 $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 2 ]
}

@test "Delete identity" {
    identity1=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    identity2=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity --delete $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
}

@test "Delete many identities" {
    identity1=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    identity2=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity --delete $identity1 $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 0 ]
}
