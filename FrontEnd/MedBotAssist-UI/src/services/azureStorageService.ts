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
      // 1. Upload file to Azure Storage
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

      // 2. Clear existing vectors
      await this.clearVectors();

      // 3. Revectorize all files
      await this.revectorizeAll();

    } catch (error) {
      throw error;
    }
  }

  private async clearVectors(): Promise<void> {
    const aiBaseUrl = process.env.REACT_APP_AI_API_BASE_URL;
    const clearUrl = `${aiBaseUrl}/api/v1/vectorization/clear-vectors`;
    const token = TokenManager.getToken();

    try {
      const response = await fetch(clearUrl, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to clear vectors: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      throw error;
    }
  }

  private async revectorizeAll(): Promise<void> {
    const aiBaseUrl = process.env.REACT_APP_AI_API_BASE_URL;
    const revectorizeUrl = `${aiBaseUrl}/api/v1/vectorization/revectorize-all`;
    const token = TokenManager.getToken();

    try {
      const response = await fetch(revectorizeUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to revectorize files: ${response.status} ${response.statusText}`);
      }
      
      await response.text();
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
      // 1. Delete file from Azure Storage
      const response = await fetch(url, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Failed to delete file: ${response.status} ${response.statusText}`);
      }

      // 2. Clear existing vectors
      await this.clearVectors();

      // 3. Revectorize remaining files
      await this.revectorizeAll();

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
