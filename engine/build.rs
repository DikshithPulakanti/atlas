fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto_dir = "../proto";
    let protos = &[
        "../proto/atlas/v1/schema.proto",
        "../proto/atlas/v1/common.proto",
        "../proto/atlas/v1/query.proto",
        "../proto/atlas/v1/results.proto",
        "../proto/atlas/v1/execution.proto",
    ];

    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(protos, &[proto_dir])?;

    // Re-run if any proto file changes
    for proto in protos {
        println!("cargo:rerun-if-changed={proto}");
    }

    Ok(())
}
