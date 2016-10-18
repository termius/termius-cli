#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "host help by arg" {
    run serverauditor host --help
    [ "$status" -eq 0 ]
}

@test "host help command" {
    run serverauditor help host
    [ "$status" -eq 0 ]
}

@test "Add general host" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    host=${lines[1]}
    [ "$(get_model_field 'host_set' $host 'label')" = '"test"' ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"localhost"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2022 ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"root"' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Add host to group" {
    group=$(serverauditor group --port 2022)
    run serverauditor host -L test --group $group --address localhost --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    host=${lines[1]}
    [ "$(get_model_field 'host_set' $host 'label')" = '"test"' ]
    [ $(get_model_field 'host_set' $host 'group') = $group ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"localhost"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') = 'null' ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ $(get_model_field 'identity_set' $identity 'username') = 'null' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Add many hosts" {
    run serverauditor host -L test_1 --port 2022 --address 127.0.0.1 --username root --password 'pa$$word'
    run serverauditor host -L test_2 --port 2222 --address google.com --username root --password 'password'
    run serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 3 ]
}

@test "Update host" {
    host=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --address google --username ROOT --password '' $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ "$(get_model_field 'host_set' $host 'label')" = '"test_3"' ]
    [ $(get_model_field 'host_set' $host 'group') = 'null' ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"google"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 22 ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"ROOT"' ]
    [ "$(get_model_field 'identity_set' $identity 'password')" = '""' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update host add to group" {
    group=$(serverauditor group --port 2022)
    host=$(serverauditor host --address localhost -L test)
    run serverauditor host --group $group $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    [ "$(get_model_field 'host_set' $host 'label')" = '"test"' ]
    [ $(get_model_field 'host_set' $host 'group') = $group ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"localhost"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') = 'null' ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ $(get_model_field 'identity_set' $identity 'username') = 'null' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update host assign visible identity" {
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    host=$(serverauditor host --address localhost -L 'test' --port 2 --username 'use r name')
    run serverauditor host --identity $identity $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ "$(get_model_field 'host_set' $host 'label')" = '"test"' ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"localhost"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2 ]
    [ $(get_model_field 'sshconfig_set' $ssh_config 'identity') = "$identity" ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update host update visible identity" {
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    host=$(serverauditor host -L 'test' --address local --identity $identity)
    run serverauditor host --username 'use r name' $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    [ "$(get_model_field 'host_set' $host 'label')" = '"test"' ]
    [ "$(get_model_field 'host_set' $host 'address')" = '"local"' ]
    ssh_config=$(get_model_field 'host_set' $host 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') = 'null' ]
    result_identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ $result_identity != $identity ]
    [ $(get_model_field 'identity_set' $result_identity 'label') = 'null' ]
    [ "$(get_model_field 'identity_set' $result_identity 'username')" = '"use r name"' ]
    [ $(get_model_field 'identity_set' $result_identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $result_identity 'ssh_key') = 'null' ]
}

@test "Update many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' $host1 $hots2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "Update hosts with same name" {
    host1=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' 'test_3'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "Delete host" {
    host1=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host1
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Delete many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host1 $host2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 0 ]
}

@test "Create with tag" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 1 ]
    [ $(get_models_set_length 'taghost_set') -eq 1 ]
    host=${lines[1]}
    assert_host_has_tag $host 'A'
}

@test "Create with 3 tags" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]

    host=${lines[1]}
    assert_host_has_tag $host 'A'
    assert_host_has_tag $host 'B'
    assert_host_has_tag $host 'C'
}

@test "Create 2 hosts with 3 tags" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    host1=${lines[1]}
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    [ "$status" -eq 0 ]
    host2=${lines[1]}
    ! [ $host1 -eq $host2 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 6 ]

    assert_host_has_tag $host1 'A'
    assert_host_has_tag $host1 'B'
    assert_host_has_tag $host1 'C'
    assert_host_has_tag $host2 'A'
    assert_host_has_tag $host2 'B'
    assert_host_has_tag $host2 'C'
}

@test "Update host with 3 same tags" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C)
    run serverauditor host -t A -t B -t C $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]

    assert_host_has_tag $host 'A'
    assert_host_has_tag $host 'B'
    assert_host_has_tag $host 'C'
}

@test "Update host with 3 diff tags" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C)
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t D -t E -t F $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 6 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]

    assert_host_has_tag $host 'D'
    assert_host_has_tag $host 'E'
    assert_host_has_tag $host 'F'
    [ $(get_model_field 'tag_set' '"A"' 'label' 'label') = '"A"' ]
    [ $(get_model_field 'tag_set' '"B"' 'label' 'label') = '"B"' ]
    [ $(get_model_field 'tag_set' '"C"' 'label' 'label') = '"C"' ]
}

assert_host_has_tag() {
    tag=$(get_model_field 'tag_set' "\"$2\"" 'id' 'label')
    [ $(get_model_field 'tag_set' $tag 'label') = "\"$2\"" ]
    hosts="$(get_model_field 'taghost_set' $tag 'host' 'tag')"
    [ -z "${hosts##*$1*}" ]
}
