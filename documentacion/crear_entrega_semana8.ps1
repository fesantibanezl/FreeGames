# Empaqueta los archivos versionados y este script del árbol de trabajo actual.
# Ejecutar desde cualquier ubicación; no realiza commit, push ni envío al AVA.
$ErrorActionPreference = 'Stop'

$repositorio = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$salida = Join-Path $repositorio 'e3_felipe_santibañez_s3.zip'
if (Test-Path -LiteralPath $salida) {
    throw "Ya existe $salida. Revísalo y cámbiale el nombre antes de generar otro paquete."
}

$rutaGit = $repositorio.Replace('\', '/')
$archivos = @(& git -C $repositorio -c "safe.directory=$rutaGit" -c core.quotepath=false ls-files --cached)
if ($LASTEXITCODE -ne 0 -or $archivos.Count -eq 0) {
    throw 'No se pudo obtener la lista de archivos versionados.'
}
$esteScript = 'documentacion/crear_entrega_semana8.ps1'
if ($archivos -cnotcontains $esteScript) {
    $archivos += $esteScript
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::Open($salida, 'Create')
try {
    foreach ($relativo in $archivos) {
        $origen = Join-Path $repositorio $relativo
        if (-not (Test-Path -LiteralPath $origen -PathType Leaf)) {
            throw "Falta un archivo versionado: $relativo"
        }
        $nombreEntrada = 'FreeGames/' + $relativo.Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip, $origen, $nombreEntrada,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $zip.Dispose()
}

$comprobacion = [System.IO.Compression.ZipFile]::OpenRead($salida)
try {
    $entradas = @($comprobacion.Entries | ForEach-Object { $_.FullName })
    $obligatorios = @(
        'FreeGames/manage.py',
        'FreeGames/requirements.txt',
        'FreeGames/README.md',
        'FreeGames/ENLACE_GITHUB.txt',
        'FreeGames/base_datos/01_estructura_oracle.sql',
        'FreeGames/base_datos/02_datos_iniciales.sql'
    )
    foreach ($obligatorio in $obligatorios) {
        if ($entradas -cnotcontains $obligatorio) {
            throw "El comprimido no contiene $obligatorio"
        }
    }
    if ($entradas.Count -ne $archivos.Count) {
        throw 'El número de entradas del comprimido no coincide con los archivos versionados.'
    }
    Write-Output "Comprimido verificado: $salida"
    Write-Output "Archivos incluidos: $($entradas.Count)"
}
finally {
    $comprobacion.Dispose()
}
