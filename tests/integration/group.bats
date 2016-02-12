#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "group help by arg" {
    run serverauditor group --help
    [ $status -eq 0 ]
}

@test "group help command" {
    run serverauditor help group
    [ $status -eq 0 ]
}

@test "Add general group" {
    run serverauditor group -L 'Group' --port 2202 --username 'use r name' --debug
    [ $status -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    group=${lines[1]}
    [ $(get_model_field 'group_set' $group 'label') = '"Group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2202 ]
    ssh_identity=$(get_model_field 'sshconfig_set' $ssh_config 'ssh_identity')
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'username') = '"use r name"' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'is_visible') = 'false' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'ssh_key') = 'null' ]
}

@test "Add group to main group" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --port 22 --parent-group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 2 ]
    created_group=${lines[1]}
    [ $(get_model_field 'group_set' $created_group 'parent_group') = "$group" ]
}

@test "Update group assign visible identity" {
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --ssh-identity $identity $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    [ $(get_model_field 'group_set' $group 'label') = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2 ]
    [ $(get_model_field 'sshconfig_set' $ssh_config 'ssh_identity') = "$identity" ]
    [ $(get_model_field 'sshidentity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'sshidentity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update group update visible identity" {
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    group=$(serverauditor group -L 'test group' --ssh-identity $identity)
    run serverauditor group --username 'use r name' $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 2 ]
    [ $(get_model_field 'group_set' $group 'label') = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') = 'null' ]
    ssh_identity=$(get_model_field 'sshconfig_set' $ssh_config 'ssh_identity')
    [ $ssh_identity != $identity ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'label') = 'null' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'username') = '"use r name"' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'is_visible') = 'false' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'ssh_key') = 'null' ]
}

@test "Update group" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --username 'user' $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 1 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
    [ $(get_model_field 'group_set' $group 'label') = '"test group"' ]
    ssh_config=$(get_model_field 'group_set' $group 'ssh_config')
    [ $(get_model_field 'sshconfig_set' $ssh_config 'port') -eq 2 ]
    ssh_identity=$(get_model_field 'sshconfig_set' $ssh_config 'ssh_identity')
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'username') = '"user"' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'is_visible') = 'false' ]
    [ $(get_model_field 'sshidentity_set' $ssh_identity 'ssh_key') = 'null' ]
}

@test "Update group add in self" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'name')
    run serverauditor group --parent-group $group $group
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Update group add into infinite loop" {
    grand_parent_group=$(serverauditor group -L 'test group' --port 2 --username 'name')
    parent_group=$(serverauditor group -L 'test group' --port 2 --username 'name' --parent-group $grand_parent_group)
    group=$(serverauditor group -L 'test group' --port 2 --username 'name' --parent-group $parent_group)
    run serverauditor group -L 'test group' --port 2 --username 'user' --parent-group $group $grand_parent_group
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'group_set') -eq 3 ]
}

@test "Update group add in parent group" {
    parent_group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group=$(serverauditor group -L 'Group' --port 2 --username 'name')
    run serverauditor group --parent-group $parent_group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
    [ $(get_models_set_length 'sshconfig_set') -eq 2 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 2 ]
    [ $(get_model_field 'group_set' $group 'parent_group') = "$parent_group" ]
    [ $(get_model_field 'group_set' $group 'label') = '"Group"' ]
}

@test "Update many groups" {
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "Delete group" {
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group1
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Delete many groups" {
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 0 ]
}
