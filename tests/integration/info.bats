#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "info help by arg" {
    run termius info --help
    [ "$status" -eq 0 ]
}

@test "info help command" {
    run termius help info
    [ "$status" -eq 0 ]
}

@test "info host use default formatter" {
    host=$(termius host -L test --port 2022 --address localhost --username root)
    run termius info $host
    [ "$status" -eq 0 ]
}

@test "info host use ssh formatter" {
    host=$(termius host -L test --port 2022 --address localhost --username root)
    run termius info $host -f ssh
    [ "$status" -eq 0 ]
}

@test "info host use ssh formatter with exta options" {
    host=$(termius host -L test --strict-host-key-check yes --keep-alive-packages 20 --timeout 100 --use-ssh-key no --port 2022 --address localhost --username root)
    termius settings --agent-forwarding yes
    run termius info $host -f ssh
    echo ${lines[*]} >&2
    cat ~/.termius/storage | jq . >&2
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o StrictHostKeyChecking=yes -o IdentitiesOnly=no -o ServerAliveInterval=100 -o ServerAliveCountMax=20 -o ForwardAgent=yes root@localhost" ]
}

@test "info host use ssh formatter with exta options disable agent forwarding" {
    host=$(termius host -L test --strict-host-key-check yes --keep-alive-packages 20 --timeout 100 --use-ssh-key no --port 2022 --address localhost --username root)
    termius settings --agent-forwarding no
    run termius info $host -f ssh
    echo ${lines[*]} >&2
    cat ~/.termius/storage | jq . >&2
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o StrictHostKeyChecking=yes -o IdentitiesOnly=no -o ServerAliveInterval=100 -o ServerAliveCountMax=20 -o ForwardAgent=no root@localhost" ]
}
@test "info group use default formatter" {
    group=$(termius group -L test --port 2022)
    run termius info --group $group --debug
    [ "$status" -eq 0 ]
}

@test "info group use ssh formatter" {
    group=$(termius group -L test --port 2022)
    run termius info --group $group -f ssh
    [ "$status" -eq 0 ]
}

@test "info host in 2 groups" {
    termius settings --agent-forwarding yes
    grandgroup=$(termius group -L test --port 22)
    group=$(termius group --parent-group $grandgroup -L test --port 2022)
    host=$(termius host --group $group --address localhost -L test)
    run termius info $host -f ssh
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o ForwardAgent=yes localhost" ]
}

@test "info host in 2 groups without agent forwarding" {
    termius settings --agent-forwarding no
    grandgroup=$(termius group -L test --port 22)
    group=$(termius group --parent-group $grandgroup -L test --port 2022)
    host=$(termius host --group $group --address localhost -L test)
    run termius info $host -f ssh
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o ForwardAgent=no localhost" ]
}

@test "info host in 2 groups with visible identity" {
    termius settings --agent-forwarding yes
    identity=$(termius identity --username user -L identity)
    grandgroup=$(termius group -L test --port 22 --identity $identity)
    group=$(termius group --parent-group $grandgroup -L test --port 2022 --username local)
    host=$(termius host --group $group --address localhost -L test --username root)
    run termius info $host -f ssh --debug
    echo "${lines[*]}" >&2
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o ForwardAgent=yes user@localhost" ]
}

@test "info host in 2 groups with visible identity without agent forwarding" {
    termius settings --agent-forwarding no
    identity=$(termius identity --username user -L identity)
    grandgroup=$(termius group -L test --port 22 --identity $identity)
    group=$(termius group --parent-group $grandgroup -L test --port 2022 --username local)
    host=$(termius host --group $group --address localhost -L test --username root)
    run termius info $host -f ssh --debug
    echo "${lines[*]}" >&2
    [ "$status" -eq 0 ]
    [ "${lines[0]}" = "ssh -p 2022 -o ForwardAgent=no user@localhost" ]
}

@test "info host not existed" {
    group=$(termius group -L test --port 2022)
    run termius info $group
    [ "$status" -eq 1 ]
}

@test "info group not existed" {
    host=$(termius host -L test --port 2022 --address localhost --username root)
    run termius info --group $host
    [ "$status" -eq 1 ]
}
