#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "pfrule help by arg" {
    run serverauditor pfrule --help
    [ "$status" -eq 0 ]
}

@test "pfrule help command" {
    run serverauditor help pfrule
    [ "$status" -eq 0 ]
}

@test "Add local pfrule" {
    host=$(serverauditor host --label test2 --address local)
    run serverauditor pfrule --local --host $host --binding 2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"L"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "null" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = '2' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "2222" ]
}

@test "Add remote pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host --binding 2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"R"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "null" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "2222" ]
}

@test "Add dynamic pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host --binding 2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"D"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "null" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2222" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "null" ]
}

@test "Add local pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --local --host $host --binding local:2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"L"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "\"local\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "2222" ]
}

@test "Add remote pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host --binding localhost:2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"R"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "\"localhost\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "2222" ]
}

@test "Add dynamic pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host --binding 127.0.0.1:2222
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"D"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2222" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "null" ]
}

@test "Update local pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    pfrule=$(serverauditor pfrule --local --host $host --binding local:2:127.0.0.1:2222)
    run serverauditor pfrule --binding local:2:127.0.0.1:2200 $pfrule
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
    pfrule=${lines[1]}
    [ $(get_model_field 'pfrule_set' $pfrule 'pf_type') = '"L"' ]
    [ $(get_model_field 'pfrule_set' $pfrule 'host') = $host ]
    [ $(get_model_field 'pfrule_set' $pfrule 'bound_address') = "\"local\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'local_port') = "2" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'hostname') = "\"127.0.0.1\"" ]
    [ $(get_model_field 'pfrule_set' $pfrule 'remote_port') = "2200" ]
}

@test "Update many remote pfrules" {
    host1="$(serverauditor host --label test2 --address 127.0.0.1)"
    pfrule1=$(serverauditor pfrule --remote --host $host1 --binding localhost:2:127.0.0.1:2222)
    pfrule2=$(serverauditor pfrule --remote --host $host1 --binding localhost:2:127.0.0.1:2220)
    host2="$(serverauditor host --label test3 --address 127.0.0.2)"
    run serverauditor pfrule --host $host2 $pfrule1 $pfrule2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 2 ]
}

@test "Delete local pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    pfrule=$(serverauditor pfrule --local --host $host --binding local:2:127.0.0.1:2222)
    run serverauditor pfrule --delete $pfrule
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Delete many remote pfrules" {
    host1="$(serverauditor host --label test2 --address 127.0.0.1)"
    pfrule1=$(serverauditor pfrule --remote --host $host1 --binding localhost:2:127.0.0.1:2222)
    pfrule2=$(serverauditor pfrule --remote --host $host1 --binding localhost:2:127.0.0.1:2220)
    run serverauditor pfrule --delete $pfrule1 $pfrule2 --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Not add local pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --local --host $host --binding 127.0.0.1:2222
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Not add remote pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host --binding 127.0.0.1:2222
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Not add dynamic pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host --binding 127.0.0.1:2222.13
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Not add remote pfrule require host" {
    run serverauditor pfrule --remote --binding localhost:2:127.0.0.1:2222
    [ "$status" -eq 1 ]
    ! [ -f  ~/.serverauditor/storage ]
}

@test "Not add remote pfrule require pf_type" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --host $host --binding localhost:2:127.0.0.1:2222
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'pfrule_set') -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}
