use pyo3::prelude::*;
use rust_jarm::Jarm;

#[pyfunction]
fn compute_jarm_hash(host: String, host_port: Option<String>) -> PyResult<String> {
    let port = host_port.unwrap_or("443".to_string());
    let result = Jarm::new(host, port).hash();
    let hash = result.unwrap_or("00000000000000000000000000000000000000000000000000000000000000".to_string());
    Ok(hash)
}

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_jarm_hash, m)?)?;
    Ok(())
}
