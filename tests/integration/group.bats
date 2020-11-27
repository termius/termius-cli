#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "group help by arg" {
    run termius group --help
    [ $status -eq 0 ]
}

@test "group help command" {
    run termius help group
    [ $status -eq 0 ]
}

@test "Add general group" {
    run termius group -L 'Group' --port 2202 --username 'use r name' --debug
    [ $status -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    group=${lines[1]}
    [ "$(get_model_field 'group_set' $group 'label')" = '"Group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2202 ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"use r name"' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Add group to main group" {
    group=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group --port 22 --parent-group $group -L subgroup
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    created_group=${lines[1]}
    [ $(get_model_field 'group_set' $created_group 'parent_group') = "$group" ]
}

@test "Update group assign visible identity" {
    identity=$(termius identity -L local --username 'ROOT')
    group=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group --identity $identity $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ "$(get_model_field 'group_set' $group 'label')" = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2 ]
    [ $(get_model_field 'sshconfig_set' $ssh_config 'identity') = "$identity" ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update group update visible identity" {
    identity=$(termius identity -L local --username 'ROOT')
    group=$(termius group -L 'test group' --identity $identity)
    run termius group --username 'use r name' $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    [ "$(get_model_field 'group_set' $group 'label')" = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') = 'null' ]
    result_identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ $result_identity != $identity ]
    [ $(get_model_field 'identity_set' $result_identity 'label') = 'null' ]
    [ "$(get_model_field 'identity_set' $result_identity 'username')" = '"use r name"' ]
    [ $(get_model_field 'identity_set' $result_identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $result_identity 'ssh_key') = 'null' ]
}

@test "Update group" {
    group=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group --username 'user' $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ "$(get_model_field 'group_set' $group 'label')" = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2 ]
    identity=$(get_model_field 'sshconfig_set' $ssh_config 'identity')
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"user"' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'false' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update group add in self" {
    group=$(termius group -L 'test group' --port 2 --username 'name')
    run termius group --parent-group $group $group
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Update group add into infinite loop" {
    grand_parent_group=$(termius group -L 'test group' --port 2 --username 'name')
    parent_group=$(termius group -L 'test group' --port 2 --username 'name' --parent-group $grand_parent_group)
    group=$(termius group -L 'test group' --port 2 --username 'name' --parent-group $parent_group)
    run termius group -L 'test group' --port 2 --username 'user' --parent-group $group $grand_parent_group
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'group_set') -eq 3 ]
}

@test "Update group add in parent group" {
    parent_group=$(termius group -L 'test group' --port 2 --username 'use r name')
    group=$(termius group -L 'Group' --port 2 --username 'name')
    run termius group --parent-group $parent_group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
    [ $(get_model_field 'group_set' $group 'parent_group') = "$parent_group" ]
    [ "$(get_model_field 'group_set' $group 'label')" = '"Group"' ]
}

@test "Update many groups" {
    group1=$(termius group -L 'test group' --port 2 --username 'use r name')
    group2=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group -L 'test group' --port 2 --username 'user' $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "Delete group" {
    group1=$(termius group -L 'test group' --port 2 --username 'use r name')
    group2=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group --delete $group1
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Delete many groups" {
    group1=$(termius group -L 'test group' --port 2 --username 'use r name')
    group2=$(termius group -L 'test group' --port 2 --username 'use r name')
    run termius group --delete $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 0 ]
}
