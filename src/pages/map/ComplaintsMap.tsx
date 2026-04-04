import { useCallback, useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import { useUser } from '@stackframe/stack';
import toast from 'react-hot-toast';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import L from 'leaflet';
import 'leaflet.markercluster';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { MapPin } from 'lucide-react';
import { getApiBase } from '../../lib/apiBase';
import { buildAuthHeaders } from '../../lib/apiHeaders';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const API_BASE = getApiBase();

type Complaint = {
  id: string;
  category?: string;
  description?: string;
  lat: number;
  lng: number;
  votes?: number;
};

function MapClickHandler({
  enabled,
  onPick,
}: {
  enabled: boolean;
  onPick: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      if (enabled) onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function ClusteredMarkers({ items }: { items: Complaint[] }) {
  const map = useMap();
  useEffect(() => {
    const mcg = (L as unknown as { markerClusterGroup: (o?: object) => L.LayerGroup }).markerClusterGroup({
      chunkedLoading: true,
    });
    items.forEach((c) => {
      if (typeof c.lat !== 'number' || typeof c.lng !== 'number') return;
      const m = L.marker([c.lat, c.lng]);
      m.bindPopup(
        `<div class="text-xs"><strong>${c.category || 'Жалоба'}</strong><br/>${(c.description || '').slice(0, 220)}<br/><span class="text-slate-500">👍 ${c.votes ?? 0}</span></div>`
      );
      mcg.addLayer(m);
    });
    map.addLayer(mcg);
    return () => {
      map.removeLayer(mcg);
    };
  }, [map, items]);
  return null;
}

export function ComplaintsMap() {
  const stackUser = useUser();
  const center: [number, number] = [51.1801, 71.446];
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [pickMode, setPickMode] = useState(false);
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [picked, setPicked] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [formSuccess, setFormSuccess] = useState(false);

  const load = useCallback(async () => {
    try {
      const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
      const res = await fetch(`${API_BASE}/api/complaints/`, { headers });
      const json = (await res.json()) as { data?: Complaint[] };
      const rows = json.data || [];
      setComplaints(rows.filter((r) => typeof r.lat === 'number' && typeof r.lng === 'number'));
    } catch {
      toast.error('Не удалось загрузить жалобы');
    }
  }, [stackUser]);

  useEffect(() => {
    void load();
  }, [load]);

  const submit = async () => {
    if (!picked) {
      toast.error('Включите «Указать на карте» и кликните по месту');
      return;
    }
    if (!category.trim() || description.trim().length < 3) {
      toast.error('Укажите категорию и описание');
      return;
    }
    setLoading(true);
    try {
      const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
      const res = await fetch(`${API_BASE}/api/complaints/`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category.trim(),
          description: description.trim(),
          lat: picked.lat,
          lng: picked.lng,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      toast.success('Жалоба добавлена');
      setFormSuccess(true);
      setCategory('');
      setDescription('');
      setPicked(null);
      setPickMode(false);
      await load();
      window.setTimeout(() => setFormSuccess(false), 8000);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Ошибка отправки');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-10rem)] md:h-[calc(100vh-6rem)] rounded-[2rem] overflow-hidden border border-slate-200 shadow-sm relative z-0">
      <div className="absolute top-4 left-4 z-[500] bg-white/95 backdrop-blur-md p-5 rounded-2xl shadow-xl border border-white/50 w-[min(100%-2rem,22rem)] max-h-[calc(100%-2rem)] overflow-y-auto">
        <h3 className="font-bold text-navy text-lg mb-1">Карта жалоб</h3>
        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
          Кластеры по районам. Укажите точку на карте, затем заполните форму.
        </p>
        {formSuccess && (
          <div
            className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm font-medium text-emerald-900"
            role="status"
          >
            Форма успешно отправлена. Жалоба появится на карте.
            <button
              type="button"
              className="ml-2 text-xs text-emerald-700 underline underline-offset-2"
              onClick={() => setFormSuccess(false)}
            >
              Скрыть
            </button>
          </div>
        )}
        <div
          className={`mb-3 rounded-xl px-3 py-2 text-[11px] font-medium ${
            pickMode ? 'bg-cyan/15 text-navy border border-cyan/30' : 'bg-slate-50 text-slate-600 border border-slate-200'
          }`}
        >
          {picked
            ? `Точка: ${picked.lat.toFixed(5)}, ${picked.lng.toFixed(5)}`
            : 'Точка не выбрана'}
        </div>
        <Button
          type="button"
          variant={pickMode ? 'primary' : 'outline'}
          className="w-full text-xs h-10 mb-4"
          onClick={() => {
            setPickMode((v) => !v);
            if (pickMode) toast('Режим выбора выключен');
            else toast('Кликните по карте, чтобы поставить метку');
          }}
        >
          <MapPin className="w-4 h-4 mr-1" />
          {pickMode ? 'Готово (выкл. выбор)' : 'Указать на карте'}
        </Button>
        <div className="space-y-3">
          <Input label="Категория" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Дорога, двор, освещение…" />
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Описание</label>
            <textarea
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm min-h-[72px]"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Опишите проблему"
            />
          </div>
        </div>
        <Button type="button" className="w-full mt-4" onClick={() => void submit()} disabled={loading}>
          {loading ? 'Отправка…' : 'Отправить жалобу'}
        </Button>
      </div>

      <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', zIndex: 0 }}>
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">Carto</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        <MapClickHandler
          enabled={pickMode}
          onPick={(lat, lng) => {
            setPicked({ lat, lng });
            setPickMode(false);
            toast.success('Точка сохранена');
          }}
        />
        <ClusteredMarkers items={complaints} />
      </MapContainer>
    </div>
  );
}
