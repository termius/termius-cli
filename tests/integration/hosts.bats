#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "hosts help by arg" {
    run termius hosts --help
    [ "$status" -eq 0 ]
}

@test "hosts help command" {
    run termius help hosts
    [ "$status" -eq 0 ]
}

@test "List hosts in table format" {
    termius host -L test --port 2022 --address 123.2.3.2 --username root --password password
    run termius hosts
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "List hosts filter by tag" {
    termius host -L test --port 2022 --address localhost --username root --password password
    host_id=$(termius host -L test --port 2022 --address localhost --username root --password password -t A)

    run termius hosts --tag A -f csv -c id
    [ "$status" -eq 0 ]
    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "List hosts in a group" {
    group=$(termius group --port 2022 -L group)
    termius host -L test --address localhost --username root --password password
    host_id=$(termius host -L test --group $group --address localhost --username root --password password)

    run termius hosts --group $group -f csv -c id
    [ "$status" -eq 0 ]

    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "List hosts in the root group" {
    group=$(termius group --port 2022 -L group)
    host_id=$(termius host -L test --group $group --address localhost --username root --password password)

    run termius hosts -f csv -c id
    [ "$status" -eq 0 ]

    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "List hosts in child groups, too" {
    group=$(termius group --port 2022 -L group)
    child_group=$(termius group --parent-group $group --port 2022 -L subgroup)
    termius host -L test --address localhost --username root --password password
    host_id=$(termius host -L test --group $child_group --address localhost --username root --password password)

    run termius hosts --group $group -f csv -c id
    [ "$status" -eq 0 ]

    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "List hosts only in child groups" {
    group=$(termius group --port 2022 -L group)
    child_group=$(termius group --parent-group $group --port 2022 -L subgroup)
    termius host -L test --address localhost --username root --password password
    termius host -L test --group $group --address localhost --username root --password password
    host_id=$(termius host -L test --group $child_group --address localhost --username root --password password)

    run termius hosts --group $child_group -f csv -c id
    [ "$status" -eq 0 ]

    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 3 ]
}

@test "List hosts in a group filter by the tag" {
    group=$(termius group --port 2022 -L group)
    host_id=$(termius host -L test --group $group --address localhost --username root --password password -t A)
    termius host -L test --address localhost --username root --password password -t A

    run termius hosts --tag A --group $group -f csv -c id
    [ "$status" -eq 0 ]
    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "List hosts filter by a tag acrous all gropus" {
    group=$(termius group --port 2022 -L group)
    host_id=$(termius host -L test --group $group --address localhost --username root --password password -t A)

    run termius hosts --tag A -f csv -c id
    [ "$status" -eq 0 ]
    [ "${lines[1]}" = "$host_id" ]
    [ "${lines[2]}" = "" ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}
