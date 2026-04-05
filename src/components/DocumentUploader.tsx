/**
 * Компонент для загрузки документов и AI заполнения форм для ЦОН
 */

import React, { useState } from 'react';
import { Upload, FileText, Loader, CheckCircle, AlertCircle, X } from 'lucide-react';
import { Card } from './ui/Card';
import { apiClient, formatApiError } from '../lib/apiClient';
import '../styles/DocumentUploader.css';

interface UploadedFile {
  id: string;
  name: string;
  type: string;
  status: 'uploading' | 'extracted' | 'filled' | 'error';
  extractedData?: Record<string, any>;
  filledForm?: Record<string, any>;
  error?: string;
  serverFileId?: string;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

const DocumentUploader: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState('passport');
  const [selectedService, setSelectedService] = useState('PASSPORT');

  const unwrapPayload = (apiResponse: any) => {
    if (apiResponse && typeof apiResponse === 'object' && apiResponse.data && typeof apiResponse.data === 'object') {
      return apiResponse.data;
    }
    return apiResponse;
  };

  // Добавить уведомление
  const addNotification = (type: 'success' | 'error' | 'info', message: string) => {
    const id = Date.now().toString();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 5000);
  };

  const docTypes = [
    { value: 'passport', label: '🛂 Паспорт' },
    { value: 'id_card', label: '📇 Удостоверение' },
    { value: 'birth_certificate', label: '👶 Свидетельство о рождении' },
    { value: 'marriage_certificate', label: '💍 Свидетельство о браке' },
  ];

  const services = [
    { value: 'PASSPORT', label: '📜 Паспорт' },
    { value: 'ID_CARD', label: '📇 Удостоверение личности' },
    { value: 'DRIVING_LICENSE', label: '🚗 Водительское удостоверение' },
    { value: 'BENEFITS', label: '🎁 Пособие' },
  ];

  // Обработка перетаскивания файлов
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
  };

  // Обработка выбранных файлов
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (fileList: FileList) => {
    setLoading(true);

    Array.from(fileList).forEach(async (file) => {
      const fileId = `${Date.now()}-${Math.random()}`;
      const newFile: UploadedFile = {
        id: fileId,
        name: file.name,
        type: selectedDocType,
        status: 'uploading',
      };

      setFiles((prev) => [...prev, newFile]);

      try {
        // Создать FormData для загрузки
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doc_type', selectedDocType);

        // Загрузить и извлечь данные через улучшенный API client
        const data = await apiClient.postFormData<any>('/api/documents/extract-ai', formData);
        const payload = unwrapPayload(data);

        if (data.success) {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    status: 'extracted',
                    extractedData: payload.extracted_data ?? data.extracted_data,
                    serverFileId: payload.file_id ?? data.file_id,
                  }
                : f
            )
          );
          addNotification('success', `✅ ${file.name}: данные извлечены успешно`);
        } else {
          throw new Error(data.message || 'Ошибка при извлечении данных');
        }
      } catch (error) {
        const errorMessage = formatApiError(error);
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? {
                  ...f,
                  status: 'error',
                  error: errorMessage,
                }
              : f
          )
        );
        addNotification('error', `❌ ${file.name}: ${errorMessage}`);
      }
    });

    setLoading(false);
  };

  // Заполнить форму
  const fillForm = async (fileId: string) => {
    const file = files.find((f) => f.id === fileId);
    if (!file || !file.serverFileId) return;

    try {
      const data = await apiClient.post<any>(
        `/api/documents/${file.serverFileId}/fill-form?service_type=${selectedService}`
      );
      const payload = unwrapPayload(data);

      if (data.success) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? {
                  ...f,
                  status: 'filled',
                  filledForm: payload.form ?? data.form,
                }
              : f
          )
        );
        addNotification('success', `✅ Форма заполнена для ${file.name}`);
      } else {
        throw new Error(data.message || 'Ошибка при заполнении формы');
      }
    } catch (error) {
      const errorMessage = formatApiError(error);
      addNotification('error', `❌ Ошибка при заполнении: ${errorMessage}`);
    }
  };

  // Отправить форму
  const submitForm = async (fileId: string) => {
    const file = files.find((f) => f.id === fileId);
    if (!file || !file.serverFileId) return;

    try {
      const data = await apiClient.post<any>(
        `/api/documents/${file.serverFileId}/submit-form`
      );
      const payload = unwrapPayload(data);

      if (data.success) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId ? { ...f, status: 'filled' } : f
          )
        );
        addNotification('success', `✅ Заявка успешно отправлена! Номер: ${payload.application_number ?? data.application_number}`);
      } else {
        throw new Error(data.message || 'Ошибка при отправке');
      }
    } catch (error) {
      const errorMessage = formatApiError(error);
      addNotification('error', `❌ Ошибка при отправке: ${errorMessage}`);
    }
  };

  return (
    <div className="document-uploader">
      {/* Notifications Panel */}
      {notifications.length > 0 && (
        <div className="notifications-panel">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`notification notification-${notif.type}`}
            >
              <span>{notif.message}</span>
              <button
                onClick={() =>
                  setNotifications((prev) =>
                    prev.filter((n) => n.id !== notif.id)
                  )
                }
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="uploader-container">
        <h2 className="uploader-title">📎 Загрузить документы для заполнения формы ЦОН</h2>
        <p className="uploader-subtitle">
          Облако автоматически извлечет данные из документа и заполнит форму подачи в ЦОН
        </p>

        {/* Выбор типа документа */}
        <div className="uploader-section">
          <label>Тип документа:</label>
          <div className="doc-type-select">
            {docTypes.map((doc) => (
              <button
                key={doc.value}
                className={`doc-type-btn ${selectedDocType === doc.value ? 'active' : ''}`}
                onClick={() => setSelectedDocType(doc.value)}
              >
                {doc.label}
              </button>
            ))}
          </div>
        </div>

        {/* Выбор типа услуги */}
        <div className="uploader-section">
          <label>Тип услуги для заполнения:</label>
          <select
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            className="service-select"
          >
            {services.map((service) => (
              <option key={service.value} value={service.value}>
                {service.label}
              </option>
            ))}
          </select>
        </div>

        {/* Зона перетаскивания */}
        <div
          className={`upload-zone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="upload-icon" />
          <h3>Перетащите файлы сюда</h3>
          <p>или</p>
          <label className="upload-btn">
            Выберите файлы
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png,.txt"
              disabled={loading}
            />
          </label>
          <p className="file-info">Поддерживаемые форматы: PDF, JPG, PNG, TXT</p>
        </div>

        {/* Список загруженных файлов */}
        {files.length > 0 && (
          <div className="files-list">
            <h3>Загруженные документы ({files.length})</h3>
            {files.map((file) => (
              <Card key={file.id} className="file-card">
                <div className="file-header">
                  <div className="file-info-group">
                    <FileText className="file-icon" />
                    <div>
                      <p className="file-name">{file.name}</p>
                      <p className="file-type">{file.type}</p>
                    </div>
                  </div>

                  {/* Статус */}
                  {file.status === 'uploading' && (
                    <div className="status uploading">
                      <Loader className="status-icon" />
                      Загрузка...
                    </div>
                  )}
                  {file.status === 'extracted' && (
                    <div className="status extracted">
                      <CheckCircle className="status-icon" />
                      Данные извлечены
                    </div>
                  )}
                  {file.status === 'filled' && (
                    <div className="status filled">
                      <CheckCircle className="status-icon" />
                      Форма заполнена
                    </div>
                  )}
                  {file.status === 'error' && (
                    <div className="status error">
                      <AlertCircle className="status-icon" />
                      Ошибка
                    </div>
                  )}
                </div>

                {/* Извлеченные данные */}
                {file.extractedData && (
                  <div className="extracted-data">
                    <h4>Извлеченные данные:</h4>
                    <div className="data-grid">
                      {Object.entries(file.extractedData).map(([key, value]) => (
                        <div key={key} className="data-item">
                          <span className="data-key">{key}:</span>
                          <span className="data-value">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Кнопки действий */}
                <div className="file-actions">
                  {file.status === 'extracted' && (
                    <button
                      className="action-btn fill-btn"
                      onClick={() => fillForm(file.id)}
                      disabled={loading}
                    >
                      🖊️ Заполнить форму
                    </button>
                  )}
                  {file.status === 'filled' && (
                    <>
                      <button
                        className="action-btn edit-btn"
                        onClick={() => alert('Редактирование формы - скоро')}
                      >
                        ✏️ Редактировать
                      </button>
                      <button
                        className="action-btn submit-btn"
                        onClick={() => submitForm(file.id)}
                      >
                        📤 Отправить в ЦОН
                      </button>
                    </>
                  )}
                  {file.status === 'error' && (
                    <p className="error-message">{file.error}</p>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Пустое состояние */}
        {files.length === 0 && !loading && (
          <div className="empty-state">
            <p>📭 Документы еще не загружены</p>
            <p>Начните с загрузки документа, чтобы начать работу</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUploader;
