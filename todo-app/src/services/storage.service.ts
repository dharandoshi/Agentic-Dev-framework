const STORAGE_KEY = 'todo_app_data';
const STORAGE_VERSION = '1.0.0';

export interface StorageData<T> {
  version: string;
  data: T;
  timestamp: number;
}

export class StorageService {
  private static instance: StorageService;

  private constructor() {}

  static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService();
    }
    return StorageService.instance;
  }

  set<T>(key: string, data: T): void {
    try {
      if (typeof window === 'undefined') return;
      const storageData: StorageData<T> = {
        version: STORAGE_VERSION,
        data,
        timestamp: Date.now(),
      };
      localStorage.setItem(key, JSON.stringify(storageData));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
      throw new Error('Storage quota exceeded or localStorage unavailable');
    }
  }

  get<T>(key: string): T | null {
    try {
      if (typeof window === 'undefined') return null;
      const item = localStorage.getItem(key);
      if (!item) return null;

      const storageData: StorageData<T> = JSON.parse(item);
      return storageData.data;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return null;
    }
  }

  remove(key: string): void {
    try {
      if (typeof window === 'undefined') return;
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  }

  clear(): void {
    try {
      if (typeof window === 'undefined') return;
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }

  getStorageSize(): number {
    if (typeof window === 'undefined') return 0;
    let totalSize = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        totalSize += localStorage[key].length + key.length;
      }
    }
    return totalSize;
  }

  isStorageAvailable(): boolean {
    try {
      if (typeof window === 'undefined') return false;
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (e) {
      return false;
    }
  }
}