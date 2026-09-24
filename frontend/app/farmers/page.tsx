"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n/context";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  Search,
  UserPlus,
  ShieldCheck,
  RefreshCw,
  Clock,
  X,
  Loader2,
  CheckCircle2,
} from "lucide-react";
import {
  getFPOs,
  getFarmers,
  createFarmer,
  Farmer,
  FPO,
  FarmerCreatePayload,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

const DEFAULT_DISTRICT = "Erode";

interface AddFarmerForm {
  name: string;
  phone: string;
  password: string;
  village: string;
  taluk: string;
  farm_area_acres: string;
  language_preference: string;
}

const EMPTY_FORM: AddFarmerForm = {
  name: "",
  phone: "",
  password: "farmer123",
  village: "",
  taluk: "",
  farm_area_acres: "",
  language_preference: "ta",
};

export default function FarmersPage() {
  const { lang } = useLanguage();
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [fpos, setFpos] = useState<FPO[]>([]);
  const [activeFpo, setActiveFpo] = useState<FPO | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [consentFilter, setConsentFilter] = useState<"all" | "granted" | "pending">("all");
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Add farmer modal state
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<AddFarmerForm>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [fpoList, token] = await Promise.all([getFPOs(), ensureToken()]);
      setFpos(fpoList);
      const primaryFpo = fpoList[0] || null;
      setActiveFpo(primaryFpo);

      if (primaryFpo) {
        const res = await getFarmers(primaryFpo.id, token ?? undefined, searchTerm);
        setFarmers(res.farmers);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async (term: string) => {
    setSearchTerm(term);
    if (activeFpo) {
      const token = await ensureToken();
      const res = await getFarmers(activeFpo.id, token ?? undefined, term);
      setFarmers(res.farmers);
    }
  };

  const handleAddFarmer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFpo) return;
    setSubmitting(true);
    setSubmitError(null);

    try {
      const token = await ensureToken();
      if (!token) {
        setSubmitError("Authentication failed. Please refresh the page.");
        return;
      }

      const payload: FarmerCreatePayload = {
        name: form.name.trim(),
        phone: form.phone.trim(),
        password: form.password || "farmer123",
        village: form.village.trim(),
        taluk: form.taluk.trim(),
        district: DEFAULT_DISTRICT,
        farm_area_acres: parseFloat(form.farm_area_acres) || 0,
        language_preference: form.language_preference,
        consent_given: true,
        lang: form.language_preference,
        alerts_opt_in: false,
      };

      const { farmer, error } = await createFarmer(activeFpo.id, payload, token);
      if (error) {
        setSubmitError(error);
      } else {
        setSubmitSuccess(true);
        setForm(EMPTY_FORM);
        // Reload farmers list
        setTimeout(async () => {
          setSubmitSuccess(false);
          setShowModal(false);
          await loadData();
        }, 1200);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const filteredFarmers = farmers.filter((f) => {
    if (consentFilter === "granted") return Boolean(f.notice_sent_at || f.alerts_opt_in);
    if (consentFilter === "pending") return !f.notice_sent_at && !f.alerts_opt_in;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "உழவர் பதிவேடு & DPDP ஒப்புதல் நிலை" : "Farmer Directory & DPDP Consent Status"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "FPO உறுப்பினர் விவசாயிகள், பயிர் பரப்பளவு, மற்றும் வாட்ஸ்அப் DPDP ஒப்புதல் பதிவுகள்."
              : "Registered FPO member farmers, farm holdings, and DPDP consent compliance status."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={loadData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
          <Button
            size="sm"
            className="h-8"
            onClick={() => { setShowModal(true); setSubmitError(null); setSubmitSuccess(false); }}
          >
            <UserPlus className="w-3.5 h-3.5 mr-1.5" />
            {lang === "ta" ? "விவசாயி சேர்" : "Add Farmer"}
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <Input
                placeholder={
                  lang === "ta"
                    ? "பெயர், கிராமம் அல்லது வட்டம் மூலம் தேடுக..."
                    : "Search by farmer name, village, or taluk..."
                }
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9 h-10"
              />
            </div>
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <Badge
                variant={consentFilter === "all" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("all")}
              >
                {lang === "ta" ? "அனைத்து விவசாயிகள்" : "All Farmers"}
              </Badge>
              <Badge
                variant={consentFilter === "granted" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("granted")}
              >
                {lang === "ta" ? "ஒப்புதல் பெற்றவை" : "Consent Active"}
              </Badge>
              <Badge
                variant={consentFilter === "pending" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("pending")}
              >
                {lang === "ta" ? "நிலுவையில்" : "Pending"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farmer Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                {lang === "ta" ? "பதிவு செய்யப்பட்ட விவசாயிகள்" : "Registered Member Farmers"}
              </CardTitle>
              <CardDescription>
                {lang === "ta"
                  ? "DPDP சட்டம் பிரிவு 8-ன் படி வாட்ஸ்அப் முதல்-தொடர்பு அறிவிப்பு காலம் மற்றும் ஒப்புதல் தணிக்கை."
                  : "DPDP Section 8 compliance: First-contact notice timestamp & WhatsApp consent tracking."}
              </CardDescription>
            </div>
            <Badge variant="secondary">
              {filteredFarmers.length} {lang === "ta" ? "உழவர்கள்" : "Farmers"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பெயர்" : "Name"}</TableHead>
                <TableHead>{lang === "ta" ? "கிராமம் / வட்டம்" : "Village / Taluk"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலப்பரப்பு" : "Land Area"}</TableHead>
                <TableHead>{lang === "ta" ? "தொலைபேசி" : "Phone"}</TableHead>
                <TableHead>{lang === "ta" ? "DPDP ஒப்புதல் நிலை" : "DPDP Status"}</TableHead>
                <TableHead>{lang === "ta" ? "விலை அறிவிப்புகள்" : "Price Alerts"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                    {lang === "ta" ? "விவசாயிகள் பட்டியல் ஏற்றப்படுகிறது..." : "Loading farmer records..."}
                  </TableCell>
                </TableRow>
              ) : filteredFarmers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta"
                      ? "தேடலுக்குரிய விவசாயிகள் எவரும் இல்லை. மேலே 'விவசாயி சேர்' பொத்தானை கிளிக் செய்யுங்கள்."
                      : "No farmers found. Click 'Add Farmer' above to register the first one."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredFarmers.map((f) => {
                  const hasConsent = Boolean(f.notice_sent_at || f.alerts_opt_in);
                  const maskedPhone = f.phone
                    ? f.phone.replace(/(\+?\d{2,5}\s?\d{3})\d{4}/, "$1••••")
                    : "—";

                  return (
                    <TableRow key={f.id}>
                      <TableCell className="font-semibold text-foreground">
                        {f.name}
                      </TableCell>
                      <TableCell>
                        {f.village}, {f.taluk}
                      </TableCell>
                      <TableCell>
                        {f.farm_area_acres} {lang === "ta" ? "ஏக்கர்" : "acres"}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {maskedPhone}
                      </TableCell>
                      <TableCell>
                        {hasConsent ? (
                          <Badge variant="success" className="gap-1">
                            <ShieldCheck className="w-3 h-3" />
                            <span>{lang === "ta" ? "அறிவிப்பு வழங்கப்பட்டது" : "Notice Logged"}</span>
                          </Badge>
                        ) : (
                          <Badge variant="warning" className="gap-1">
                            <Clock className="w-3 h-3" />
                            <span>{lang === "ta" ? "நிலுவையில்" : "Pending First Notice"}</span>
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={f.alerts_opt_in ? "default" : "secondary"}>
                          {f.alerts_opt_in
                            ? lang === "ta" ? "இயக்கத்தில்" : "Opted-In"
                            : lang === "ta" ? "நிறுத்தப்பட்டது" : "Off"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Add Farmer Modal */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}
        >
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 relative">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition-colors"
              onClick={() => setShowModal(false)}
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-gray-900 mb-1">
              {lang === "ta" ? "புதிய விவசாயி பதிவு" : "Register New Farmer"}
            </h3>
            <p className="text-xs text-gray-500 mb-5">
              {lang === "ta"
                ? "FPO உறுப்பினராக விவசாயியை பதிவு செய்யவும். DPDP ஒப்புதல் தானாக பதிவாகும்."
                : "Register a farmer as an FPO member. DPDP consent will be logged automatically."}
            </p>

            {submitSuccess ? (
              <div className="flex flex-col items-center justify-center py-8 space-y-2 text-emerald-700">
                <CheckCircle2 className="w-10 h-10" />
                <p className="font-bold text-base">
                  {lang === "ta" ? "விவசாயி வெற்றிகரமாக சேர்க்கப்பட்டார்!" : "Farmer registered successfully!"}
                </p>
              </div>
            ) : (
              <form onSubmit={handleAddFarmer} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="col-span-2">
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "பெயர் *" : "Full Name *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "முழு பெயர்" : "e.g. Ramasamy K"}
                      value={form.name}
                      onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "தொலைபேசி *" : "Phone *"}
                    </label>
                    <Input
                      required
                      placeholder="9876543210"
                      value={form.phone}
                      onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "நிலப்பரப்பு (ஏக்கர்) *" : "Land Area (acres) *"}
                    </label>
                    <Input
                      required
                      type="number"
                      step="0.1"
                      min="0.1"
                      placeholder="2.5"
                      value={form.farm_area_acres}
                      onChange={(e) => setForm((f) => ({ ...f, farm_area_acres: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "கிராமம் *" : "Village *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "கிராமம்" : "e.g. Kodumudi"}
                      value={form.village}
                      onChange={(e) => setForm((f) => ({ ...f, village: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "வட்டம் *" : "Taluk *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "வட்டம்" : "e.g. Perundurai"}
                      value={form.taluk}
                      onChange={(e) => setForm((f) => ({ ...f, taluk: e.target.value }))}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="text-xs font-semibold text-gray-700 block mb-1">
                      {lang === "ta" ? "மொழி விருப்பம்" : "Language Preference"}
                    </label>
                    <select
                      className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                      value={form.language_preference}
                      onChange={(e) => setForm((f) => ({ ...f, language_preference: e.target.value }))}
                    >
                      <option value="ta">தமிழ் (Tamil)</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                </div>

                {submitError && (
                  <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
                    {submitError}
                  </p>
                )}

                <div className="flex items-center space-x-2 pt-2">
                  <Button type="submit" className="flex-1" disabled={submitting}>
                    {submitting ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{lang === "ta" ? "சேர்க்கப்படுகிறது..." : "Registering..."}</>
                    ) : (
                      <><UserPlus className="w-4 h-4 mr-2" />{lang === "ta" ? "விவசாயி சேர்" : "Register Farmer"}</>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                    {lang === "ta" ? "ரத்து" : "Cancel"}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
