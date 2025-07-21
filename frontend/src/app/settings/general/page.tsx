"use client";

import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LocaleSelect } from "@/components/LocaleSelect";

export default function GeneralSettingsPage() {
  const [name, setName] = useState("Jane Doe");
  const [avatar, setAvatar] = useState("/avatars/jane_doe.png");

  const handleAvatarUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAvatar(URL.createObjectURL(e.target.files[0]));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">General Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences.
        </p>
      </div>
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={avatar} />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <Input type="file" onChange={handleAvatarUpload} className="max-w-xs" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="max-w-sm"
          />
        </div>
        <div className="space-y-2">
          <Label>Theme</Label>
          <ThemeToggle />
        </div>
        <div className="space-y-2">
          <Label>Language</Label>
          <LocaleSelect />
        </div>
        <Button>Save Changes</Button>
      </div>
    </div>
  );
}
