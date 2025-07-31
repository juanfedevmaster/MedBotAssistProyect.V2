import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import AzureStorageService from '../services/azureStorageService';

interface InstructionsProps {
  doctorId: string | number | null;
  username?: string;
}

interface FileItem {
  name: string;
  lastModified: Date;
  size: number;
  contentType: string;
  url: string;
}

const Instructions: React.FC<InstructionsProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [deleteModalFile, setDeleteModalFile] = useState<FileItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Load files from Azure Storage
  const loadFiles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fileList = await AzureStorageService.listBlobs();
      setFiles(fileList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get file icon based on type
  const getFileIcon = (contentType: string): string => {
    if (contentType.includes('pdf')) return 'bi-file-earmark-pdf';
    if (contentType.includes('image')) return 'bi-file-earmark-image';
    if (contentType.includes('video')) return 'bi-file-earmark-play';
    if (contentType.includes('audio')) return 'bi-file-earmark-music';
    if (contentType.includes('text') || contentType.includes('document')) return 'bi-file-earmark-text';
    if (contentType.includes('spreadsheet') || contentType.includes('excel')) return 'bi-file-earmark-excel';
    if (contentType.includes('presentation') || contentType.includes('powerpoint')) return 'bi-file-earmark-ppt';
    return 'bi-file-earmark';
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      
      await AzureStorageService.uploadFile(selectedFile);
      
      // Reload files list
      await loadFiles();
      
      // Close modal and reset
      setIsUploadModalOpen(false);
      setSelectedFile(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  // Handle file download
  const handleDownload = async (file: FileItem) => {
    try {
      const blob = await AzureStorageService.downloadFile(file.name);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download file');
    }
  };

  // Handle file deletion
  const handleDelete = async () => {
    if (!deleteModalFile) return;

    try {
      setDeleting(true);
      setError(null);
      
      await AzureStorageService.deleteFile(deleteModalFile.name);
      
      // Reload files list
      await loadFiles();
      
      // Close modal
      setDeleteModalFile(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
    } finally {
      setDeleting(false);
    }
  };

  // Filter files based on search term
  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
          <div className="text-center text-white">
            <div className="spinner-border mb-3" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <h5>Loading instructions...</h5>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark px-4 pt-3" style={{ backgroundColor: '#405de6' }}>
        <span className="navbar-brand fw-bold text-white">MedBotAssist</span>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarMenu"
          style={{ borderColor: '#ffffff' }}
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarMenu">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/home')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-house me-2"></i>
                Home
              </button>
            </li>
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/patients')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-people me-2"></i>
                Patients
              </button>
            </li>
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/appointments')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-calendar-check me-2"></i>
                Appointments
              </button>
            </li>
            <li className="nav-item">
              <button
                className="btn nav-link fw-bold"
                style={{ 
                  border: 'none', 
                  background: 'rgba(255,255,255,0.2)', 
                  color: '#fff',
                  borderRadius: '5px'
                }}
              >
                <i className="bi bi-file-earmark-text me-2"></i>
                Instructions
              </button>
            </li>
          </ul>
          
          <ul className="navbar-nav">
            <li className="nav-item dropdown">
              <button
                className="btn dropdown-toggle d-flex align-items-center"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  color: '#fff',
                  border: '1px solid rgba(255,255,255,0.3)',
                  fontWeight: 'bold'
                }}
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="bi bi-person-circle me-2"></i>
                {username || 'Usuario'}
              </button>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <button 
                    className="dropdown-item d-flex align-items-center" 
                    onClick={() => navigate('/profile')}
                  >
                    <i className="bi bi-person me-2"></i>
                    Profile
                  </button>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button 
                    className="dropdown-item d-flex align-items-center text-danger" 
                    onClick={() => {
                      if (window.confirm('¿Estás seguro de que deseas cerrar sesión?')) {
                        navigate('/login');
                      }
                    }}
                  >
                    <i className="bi bi-box-arrow-right me-2"></i>
                    Logout
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </nav>

      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-12">
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h2 className="mb-1" style={{ color: '#405de6' }}>
                  <i className="bi bi-file-earmark-text me-2"></i>
                  Medical Instructions
                </h2>
                <p className="mb-0" style={{ color: '#405de6', opacity: 0.8 }}>
                  Manage and access medical instruction files
                </p>
              </div>
              <button 
                className="btn"
                onClick={() => setIsUploadModalOpen(true)}
                style={{
                  backgroundColor: '#405de6',
                  color: 'white',
                  border: '1px solid #405de6',
                  fontWeight: 'bold'
                }}
              >
                <i className="bi bi-cloud-upload me-2"></i>
                Upload File
              </button>
            </div>

            {/* Statistics */}
            <div className="row mb-4">
              <div className="col-md-4 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-files text-primary mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">{files.length}</h3>
                    <small className="text-muted">Total Files</small>
                  </div>
                </div>
              </div>
              <div className="col-md-4 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-hdd text-info mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">
                      {formatFileSize(files.reduce((total, file) => total + file.size, 0))}
                    </h3>
                    <small className="text-muted">Total Size</small>
                  </div>
                </div>
              </div>
              <div className="col-md-4 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-cloud-check text-success mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">Azure</h3>
                    <small className="text-muted">Cloud Storage</small>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Card */}
            <div className="card border-0 shadow-lg">
              <div className="card-header bg-white border-0 py-3">
                <div className="row align-items-center">
                  <div className="col-md-6">
                    <h5 className="mb-0">
                      <i className="bi bi-folder2-open me-2 text-primary"></i>
                      Instruction Files
                    </h5>
                  </div>
                  <div className="col-md-6">
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="bi bi-search"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Search files..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="card-body">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                {/* Files Grid */}
                {filteredFiles.length === 0 ? (
                  <div className="text-center py-5">
                    <i className="bi bi-folder-x" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
                    <h4 className="mt-3 text-muted">No files found</h4>
                    <p className="text-muted">
                      {searchTerm ? 'Try adjusting your search criteria' : 'Upload your first instruction file to get started'}
                    </p>
                  </div>
                ) : (
                  <div className="row">
                    {filteredFiles.map((file, index) => (
                      <div key={index} className="col-lg-4 col-md-6 mb-4">
                        <div className="card border-0 shadow-sm h-100">
                          <div className="card-body">
                            <div className="d-flex align-items-start mb-3">
                              <i className={`bi ${getFileIcon(file.contentType)} text-primary me-3`} 
                                 style={{ fontSize: '2rem' }}></i>
                              <div className="flex-grow-1">
                                <h6 className="card-title mb-1 text-truncate" title={file.name}>
                                  {file.name}
                                </h6>
                                <small className="text-muted">
                                  {formatFileSize(file.size)}
                                </small>
                              </div>
                            </div>
                            
                            <div className="mb-3">
                              <small className="text-muted">
                                <i className="bi bi-calendar me-1"></i>
                                {file.lastModified.toLocaleDateString()} {file.lastModified.toLocaleTimeString()}
                              </small>
                            </div>

                            <div className="d-flex gap-2">
                              <button 
                                className="btn btn-sm btn-primary flex-grow-1"
                                onClick={() => handleDownload(file)}
                              >
                                <i className="bi bi-download me-1"></i>
                                Download
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => setDeleteModalFile(file)}
                              >
                                <i className="bi bi-trash"></i>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Doctor information */}
                <div className="mt-4 p-3 bg-light rounded">
                  <small className="text-muted">
                    <i className="bi bi-info-circle me-1"></i>
                    Doctor ID: <strong>{doctorId}</strong> | 
                    Session: <strong>{username}</strong>
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {isUploadModalOpen && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-cloud-upload me-2"></i>
                  Upload Instruction File
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={() => {
                    setIsUploadModalOpen(false);
                    setSelectedFile(null);
                    setError(null);
                  }}
                ></button>
              </div>
              <div className="modal-body">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="mb-3">
                  <label className="form-label">Select File</label>
                  <input 
                    type="file" 
                    className="form-control"
                    onChange={handleFileSelect}
                    disabled={uploading}
                  />
                </div>

                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  <strong>Note:</strong> After uploading, the file will be automatically processed and vectorized for AI chat integration. This may take a few moments.
                </div>

                {selectedFile && (
                  <div className="alert alert-success">
                    <div className="d-flex align-items-center">
                      <i className={`bi ${getFileIcon(selectedFile.type)} me-2`}></i>
                      <div>
                        <strong>{selectedFile.name}</strong><br />
                        <small>{formatFileSize(selectedFile.size)}</small>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {
                    setIsUploadModalOpen(false);
                    setSelectedFile(null);
                    setError(null);
                  }}
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleUpload}
                  disabled={!selectedFile || uploading}
                >
                  {uploading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Uploading...</span>
                      </span>
                      Uploading & Processing...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-cloud-upload me-2"></i>
                      Upload File
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModalFile && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title text-danger">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Delete File
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={() => setDeleteModalFile(null)}
                ></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete this file?</p>
                <div className="alert alert-warning">
                  <div className="d-flex align-items-center">
                    <i className={`bi ${getFileIcon(deleteModalFile.contentType)} me-2`}></i>
                    <div>
                      <strong>{deleteModalFile.name}</strong><br />
                      <small>{formatFileSize(deleteModalFile.size)}</small>
                    </div>
                  </div>
                </div>
                <p className="text-danger">
                  <strong>This action cannot be undone!</strong>
                </p>
                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  <small>After deletion, the AI knowledge base will be automatically updated to remove this file's content.</small>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setDeleteModalFile(null)}
                  disabled={deleting}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger"
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  {deleting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Deleting...</span>
                      </span>
                      Deleting & Reprocessing...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-trash me-2"></i>
                      Delete File
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Instructions;
