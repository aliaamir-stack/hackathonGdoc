"use client";

import type { EmergencyIdentifyResponse, MedicineScanResponse } from "@/lib/pulse-api/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { AlertTriangle, Pill, Siren } from "lucide-react";

type Props = {
  medicine: MedicineScanResponse | null;
  medicineError: string | null;
  emergency: EmergencyIdentifyResponse | null;
  emergencyError: string | null;
};

export function MedicineEmergencyResults({ medicine, medicineError, emergency, emergencyError }: Props) {
  const showMedicine = medicine || medicineError;
  const showEmergency = emergency || emergencyError;

  if (!showMedicine && !showEmergency) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-vital">
        <span className="h-px w-8 bg-vital" />
        Analysis output
      </div>

      {showMedicine ? (
        <Card className="border-border bg-surface/40 shadow-[var(--shadow-card)]">
          <CardHeader className="border-b border-border">
            <CardTitle className="flex items-center gap-2 font-display text-lg">
              <Pill className="size-5 text-map-blue" />
              Medicine scan
              <span className="font-mono text-[10px] font-normal uppercase tracking-wider text-3">
                POST /api/medicine/scan
              </span>
            </CardTitle>
            <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
              Package / label extraction
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            {medicineError ? (
              <p className="font-mono text-sm text-alert-red">{medicineError}</p>
            ) : medicine ? (
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-wider text-3">Drug</p>
                  <p className="font-display text-2xl font-bold text-foreground">{medicine.drug_name}</p>
                </div>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-wider text-3">Dosage</p>
                  <p className="text-lg text-2">{medicine.dosage}</p>
                </div>
                <div className="sm:col-span-2">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-3">Expiry status</p>
                  <Badge variant={medicine.expired ? "destructive" : "secondary"} className="mt-1">
                    {medicine.expired ? "Possibly expired" : "Not flagged expired"}
                  </Badge>
                </div>
                <div className="sm:col-span-2">
                  <p className="mb-2 font-mono text-[10px] uppercase tracking-wider text-3">Interactions</p>
                  <ul className="flex flex-wrap gap-2">
                    {medicine.interactions?.length ? (
                      medicine.interactions.map((x) => (
                        <Badge key={x} variant="outline" className="border-alert-amber/50 text-alert-amber">
                          {x}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-3">None listed</span>
                    )}
                  </ul>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      {showEmergency ? (
        <Card className="border-border bg-surface/40 shadow-[var(--shadow-card)]">
          <CardHeader className="border-b border-border">
            <CardTitle className="flex items-center gap-2 font-display text-lg">
              <Siren className="size-5 text-alert-red" />
              Emergency protocol
              <span className="font-mono text-[10px] font-normal uppercase tracking-wider text-3">
                POST /api/emergency/identify
              </span>
            </CardTitle>
            <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
              From dispatch audio or transcript
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            {emergencyError ? (
              <p className="font-mono text-sm text-alert-red">{emergencyError}</p>
            ) : emergency ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-3">
                  <p className="font-display text-xl font-bold text-foreground">{emergency.protocol}</p>
                  {emergency.call_ambulance ? (
                    <Badge className="bg-alert-red text-primary-foreground">
                      <AlertTriangle className="mr-1 size-3" />
                      Call ambulance
                    </Badge>
                  ) : null}
                </div>
                <Separator />
                <div>
                  <p className="mb-2 font-mono text-[10px] uppercase tracking-wider text-3">Steps</p>
                  <ol className="list-decimal space-y-2 pl-5 text-sm text-2">
                    {emergency.steps?.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ol>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
