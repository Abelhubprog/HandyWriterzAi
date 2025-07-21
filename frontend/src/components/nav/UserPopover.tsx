import React from 'react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';

// Mock API call
const fetchCredits = async (): Promise<{ credits: number; wallet: string }> => {
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate network delay
  return { credits: 1234, wallet: '0xABcdeFG1234567890hIjKLMnOPQRstUVwXYZ1234' };
};

const truncateWallet = (wallet: string) => {
    if (wallet.length < 10) return wallet;
    return `${wallet.substring(0, 4)}...${wallet.substring(wallet.length - 4)}`;
}

export const UserPopover: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['userCredits'],
    queryFn: fetchCredits,
  });

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            <AvatarImage src="/avatars/01.png" alt="@shadcn" />
            <AvatarFallback>SC</AvatarFallback>
          </Avatar>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Wallet</h4>
            {isLoading ? (
              <Skeleton className="h-4 w-[250px]" />
            ) : (
              <p className="text-sm text-muted-foreground">
                {truncateWallet(data?.wallet ?? '')}
              </p>
            )}
          </div>
          <div className="grid gap-2">
            <div className="grid grid-cols-3 items-center gap-4">
              <span>Credits</span>
              {isLoading ? (
                <Skeleton className="h-4 w-[100px]" />
              ) : (
                <span className="font-semibold">{data?.credits}</span>
              )}
            </div>
            <Button>Add Credits</Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};