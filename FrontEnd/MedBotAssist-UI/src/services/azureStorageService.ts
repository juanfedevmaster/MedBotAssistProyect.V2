import TokenManager from '../utils/tokenManager';

class AzureStorageService {
  private getSasToken(): string | null {
    const token = TokenManager.getToken();
    if (!token) {
      return null;
    }
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      
      if (!payload.sasToken) {
        return null;
      }
      
      return payload.sasToken;
    } catch (error) {
      return null;
    }
  }

  private getStorageUrl(): string {
    const baseUrl = process.env.REACT_APP_AZURE_STORAGE_URL || 'https://yourstorageaccount.blob.core.windows.net';
    const containerName = process.env.REACT_APP_AZURE_CONTAINER_NAME || 'instructions';
    return `${baseUrl}/${containerName}`;
  }

  // Método para verificar la configuración
  public verifyConfiguration(): void {
    console.log('=== Azure Storage Configuration ===');
    console.log('Base URL:', process.env.REACT_APP_AZURE_STORAGE_URL);
    console.log('Container:', process.env.REACT_APP_AZURE_CONTAINER_NAME);
    
    const token = TokenManager.getToken();
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        console.log('JWT has sasToken claim:', !!payload.sasToken);
      } catch (error) {
        // Silent error
      }
    }
    console.log('=== End Configuration ===');
  }

  async listBlobs(): Promise<any[]> {
    const sasToken = this.getSasToken();
    if (!sasToken) {
      throw new Error('SAS token not found in JWT');
    }

    const storageUrl = this.getStorageUrl();
    const url = `${storageUrl}?${sasToken}&restype=container&comp=list`;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to list blobs: ${response.status} ${response.statusText}`);
      }

      const xmlText = await response.text();
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
      
      const blobs = Array.from(xmlDoc.querySelectorAll('Blob')).map(blob => {
        const name = blob.querySelector('Name')?.textContent || '';
        const lastModified = blob.querySelector('Last-Modified')?.textContent || '';
        const size = blob.querySelector('Content-Length')?.textContent || '0';
        const contentType = blob.querySelector('Content-Type')?.textContent || 'application/octet-stream';
        
        return {
          name,
          lastModified: new Date(lastModified),
          size: parseInt(size),
          contentType,
          url: `${storageUrl}/${name}?${sasToken}`
        };
      });

      return blobs;
    } catch (error) {
      throw error;
    }
  }

  async uploadFile(file: File): Promise<void> {
    const sasToken = this.getSasToken();
    if (!sasToken) {
      throw new Error('SAS token not found in JWT');
    }

    const storageUrl = this.getStorageUrl();
    const url = `${storageUrl}/${file.name}?${sasToken}`;
    
    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'x-ms-blob-type': 'BlockBlob',
          'Content-Type': file.type || 'application/octet-stream'
        },
        body: file
      });

      if (!response.ok) {
        throw new Error(`Failed to upload file: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      throw error;
    }
  }

  async deleteFile(fileName: string): Promise<void> {
    const sasToken = this.getSasToken();
    if (!sasToken) {
      throw new Error('SAS token not found in JWT');
    }

    const url = `${this.getStorageUrl()}/${fileName}?${sasToken}`;
    
    try {
      const response = await fetch(url, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Failed to delete file: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      throw error;
    }
  }

  async downloadFile(fileName: string): Promise<Blob> {
    const sasToken = this.getSasToken();
    if (!sasToken) {
      throw new Error('SAS token not found in JWT');
    }

    const url = `${this.getStorageUrl()}/${fileName}?${sasToken}`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to download file: ${response.status} ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      throw error;
    }
  }
}

const azureStorageService = new AzureStorageService();
export default azureStorageService;
